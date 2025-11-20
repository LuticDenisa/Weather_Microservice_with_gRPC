import { useEffect, useMemo, useState } from 'react';
import { fetchCurrent, fetchHistory } from './api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

function msToFull(ms) {
  return new Date(ms).toLocaleString();
}

function msToTime(ms) {
  return new Date(ms).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

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
      setError(null);
      const s = await fetchHistory(c);
      setSeries(s);
    } catch (e) {
      setError(e?.message || "Failed to load history");
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
    } catch (e) {
      setError(e?.message || "Failed to load current");
    } finally {
      setLoadingNow(false);
    }
  }

   async function fetchCurrentAndRefreshHistory() {
    await loadCurrent(city);
    await loadHistoryAuto24h(city);
  }

  useEffect(() => {
    loadHistoryAuto24h(city);
  }, []);

  const chartData = useMemo(
    () => series.map(p => ({ ...p, label: msToTime(p.timestamp_ms) })),
    [series]
  );

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto", fontFamily: "Inter, system-ui, Arial" }}>
      <h1 style={{ marginBottom: 8 }}>Weather dashboard</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="City"
          style={{ padding: 8, borderRadius: 8, border: "1px solid #ccc", flex: "0 0 240px" }}
        />
        <button
          onClick={fetchCurrentAndRefreshHistory}
          disabled={loadingNow || loadingSeries}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: "#111", color: "white", cursor: "pointer" }}
        >
          {loadingNow || loadingSeries ? "Loading..." : "Fetch current & refresh history"}
        </button>
      </div>

      {error && (
        <div style={{ background: "#ffe6e6", border: "1px solid #ffb3b3", color: "#990000", padding: 12, borderRadius: 8, marginBottom: 12 }}>
          {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
        {/* Card Current */}
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
          <h3 style={{ margin: "0 0 6px" }}>Current</h3>
          {loadingNow && <div>Loading current…</div>}
          {!loadingNow && now && (
            <div>
              <div style={{ fontSize: 18, fontWeight: 600 }}>{now.city}</div>
              <div style={{ fontSize: 30, fontWeight: 700 }}>{now.temperature_c.toFixed(1)} °C</div>
              <div style={{ color: "#666" }}>{now.description}</div>
              <div style={{ marginTop: 8, fontSize: 14 }}>
                Humidity: <b>{now.humidity}%</b> · Wind: <b>{now.wind_speed} m/s</b>
              </div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                {msToFull(now.timestamp_ms)}
              </div>
            </div>
          )}
          {!loadingNow && !now && <div style={{ color: "#666" }}>Press the button to fetch current weather.</div>}
        </div>

        {/* Summary */}
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
          <h3 style={{ margin: "0 0 6px" }}>Summary (last 24h)</h3>
          {loadingSeries && <div>Loading history…</div>}
          {!loadingSeries && series.length > 0 && (
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              <li>Points: <b>{series.length}</b></li>
              <li>Min: <b>{Math.min(...series.map(s => s.temperature_c)).toFixed(1)} °C</b></li>
              <li>Max: <b>{Math.max(...series.map(s => s.temperature_c)).toFixed(1)} °C</b></li>
            </ul>
          )}
          {!loadingSeries && series.length === 0 && <div style={{ color: "#666" }}>No data yet.</div>}
        </div>
      </div>

      {/* Chart */}
      <Chart data={chartData} />
    </div>
  );
}

function Chart({ data }) {
  return (
    <div style={{ height: 380, border: "1px solid #eee", borderRadius: 12, padding: 8 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="temperature_c" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}