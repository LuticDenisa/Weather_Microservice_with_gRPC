async function parseOrThrow(res) {
  if (res.ok) return res.json();
  const text = await res.text();
  try {
    const j = JSON.parse(text);
    throw new Error(j.detail || text || "Request failed");
  } catch {
    throw new Error(text || "Request failed");
  }
}


export async function fetchCurrent(city) {
    const res = await fetch(`/api/weather/current?city=${encodeURIComponent(city)}`);
    return parseOrThrow(res);
}

export async function fetchHistory(city, fromMs, toMs) {
    const url = new URL(`/api/weather/history`, window.location.origin);
    url.searchParams.append('city', city);
    if (fromMs) url.searchParams.set('from_ms', String(fromMs));
    if (toMs) url.searchParams.set('to_ms', String(toMs));
    const res = await fetch(url.toString());
    return parseOrThrow(res);
}