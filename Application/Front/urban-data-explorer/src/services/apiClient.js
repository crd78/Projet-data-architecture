const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

export async function getJson(path, params = {}, options = {}) {
  const url = new URL(path, API_BASE_URL);
  url.search = new URLSearchParams(params).toString();

  const res = await fetch(url.toString(), options);
  const payload = await res.json();

  if (!res.ok) {
    throw new Error(payload?.detail || `HTTP ${res.status}`);
  }

  return payload;
}