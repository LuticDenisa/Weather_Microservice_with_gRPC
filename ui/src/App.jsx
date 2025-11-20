import { useEffect, useMemo, useState } from 'react';
import { fetchCurrent, fetchHistory } from './api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import './index.css';

function msToFull(ms) { return new Date(ms).toLocaleString(); }
function msToTime(ms) { return new Date(ms).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }

export default function App() {
  const [city, setCity] = useState("London");
  const [now, setNow] = useState(null);
  const [series, setSeries] = useState([]);
  const [loadingNow, setLoadingNow] = useState(false);
  const [loadingSeries, setLoadingSeries] = useState(false);
  const [error, setError] = useState(null);

  async function loadHistoryAuto24h(c) {
    try {
      setLoadingSeries(true);
      // setError(null);
      const s = await fetchHistory(c);
      setSeries(s);
    } catch (e) {
      setNow(null);
      setError(e?.message || `Failed to load current weather.`);
    } finally {
      setLoadingSeries(false);
    }
  }

  async function loadCurrent(c) {
    try {
      setLoadingNow(true);
      setError(null);
      const data = await fetchCurrent(c);
      setNow(data);
      return true;
    } catch (e) {
      setNow(null);
      const msg = e?.message || "";
      if (msg.includes("NOT_FOUND") || msg.includes("404")) {
        setError(`City "${c}" not found.`);
      } else {
        setError(msg || "Failed to load current weather");
      }
      return false;
    } finally {
      setLoadingNow(false);
    }
  }

   async function fetchCurrentAndRefreshHistory() {
    const c = city.trim();
    if (!c) { setError("Please enter a city name."); return; }
    
    const ok = await loadCurrent(c);
    if (!ok) {
      setSeries([]);
      return;
    }
    await loadHistoryAuto24h(c);
  }

  useEffect(() => { loadHistoryAuto24h(city); }, []);

  const chartData = useMemo(
    () => series.map(p => ({ ...p, label: msToTime(p.timestamp_ms) })),
    [series]
  );

  return (
    <div className="page">
      <div className="glass">
        <h1 style={{ marginTop: 0, marginBottom: 16, textAlign: "center" }}>
          Weather dashboard
        </h1>

        <div className="header">
          <input
            className="input"
            value={city}
            onChange={(e) => { setCity(e.target.value); setError(null); }}
            onBlur={() => setCity(v => v.trim())}
            placeholder="City"
          />
          <button 
            className="button" 
            onClick={fetchCurrentAndRefreshHistory} 
            disabled={loadingNow || loadingSeries}>
            {loadingNow || loadingSeries ? "Loading..." : "Fetch current & refresh history"}
          </button>
        </div>

        {error && <div className="alert">{error}</div>}

        <div className="panels">
          <div className="panel">
            <h3 style={{ margin: "0 0 6px" }}>Current</h3>
            {loadingNow && <div>Loading current…</div>}
            {!loadingNow && now && (
              <div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>{now.city}</div>
                <div style={{ fontSize: 30, fontWeight: 700 }}>{now.temperature_c.toFixed(1)} °C</div>
                <div style={{ color: "#334155" }}>{now.description}</div>
                <div style={{ marginTop: 8, fontSize: 14 }}>
                  Humidity: <b>{now.humidity}%</b> · Wind: <b>{now.wind_speed} m/s</b>
                </div>
                <div style={{ marginTop: 6, fontSize: 12, color: "#475569" }}>
                  {msToFull(now.timestamp_ms)}
                </div>
              </div>
            )}
            {!loadingNow && !now && <div style={{ color: "#475569" }}>Press the button to fetch current weather.</div>}
          </div>

          <div className="panel">
            <h3 style={{ margin: "0 0 6px" }}>Summary (last 24h)</h3>
            {loadingSeries && <div>Loading history…</div>}
            {!loadingSeries && series.length > 0 && (
              <ul style={{ margin: 0, paddingLeft: 16 }}>
                <li>Points: <b>{series.length}</b></li>
                <li>Min: <b>{Math.min(...series.map(s => s.temperature_c)).toFixed(1)} °C</b></li>
                <li>Max: <b>{Math.max(...series.map(s => s.temperature_c)).toFixed(1)} °C</b></li>
              </ul>
            )}
            {!loadingSeries && series.length === 0 && <div style={{ color: "#475569" }}>No data yet.</div>}
          </div>
        </div>

        <div className="chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis domain={['auto','auto']} />
              <Tooltip />
              <Line type="monotone" dataKey="temperature_c" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}