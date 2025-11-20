export async function fetchCurrent(city) {
    const res = await fetch(`/api/weather/current?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

export async function fetchHistory(city, fromMs, toMs) {
    const url = new URL(`/api/weather/history`, window.location.origin);
    url.searchParams.append('city', city);
    if (fromMs) url.searchParams.set('from_ms', String(fromMs));
    if (toMs) url.searchParams.set('to_ms', String(toMs));
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}