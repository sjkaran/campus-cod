// ===== API client placeholder =====
// This module is the single integration boundary for the future FastAPI
// backend. Nothing in Stage 1 calls this for real; services currently talk
// to the mock/ layer instead. Once Stage 2 begins, services are switched to
// call this client, and no other file in the app needs to change.
//
//   Student UI -> Service -> [this file] -> FastAPI backend -> PostgreSQL

const BASE_URL = '/api'; // will become the deployed backend origin

let authToken = null;

export function setAuthToken(token) {
  authToken = token;
}

function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;
  return headers;
}

/**
 * Thin wrapper around fetch(). Not used during Stage 1 — present so the
 * shape of the future integration is explicit and reviewable now.
 */
export async function apiRequest(path, { method = 'GET', body, headers } = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: buildHeaders(headers),
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = new Error(`API request failed: ${response.status}`);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

export const apiClient = { get: (p) => apiRequest(p), post: (p, body) => apiRequest(p, { method: 'POST', body }), patch: (p, body) => apiRequest(p, { method: 'PATCH', body }) };
