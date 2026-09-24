// FUTURE API INTEGRATION: the only place that talks HTTP.
import { CONFIG } from '../config.js';
import { session } from './session.js';

export async function http(method, path, body) {
  const res = await fetch(CONFIG.API_BASE_URL + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(session.token && { Authorization: `Bearer ${session.token}` }) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) { session.clear(); location.hash = '#/login'; }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `Request failed (${res.status})`);
  return res.json();
}
