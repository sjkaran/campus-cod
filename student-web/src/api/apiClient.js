// ===== API client (Stage 2 — live backend) =====
// Single integration boundary for the FastAPI backend. Every service calls
// this; nothing else in the app builds a URL or calls fetch() directly.
//
//   Student UI -> Service -> [this file] -> FastAPI backend -> PostgreSQL
//
// Backend conventions this client understands:
//   Auth:        Authorization: Bearer <token>
//   Single item: {"data": {...}}
//   Collection:  {"data": [...], "pagination": {"page","page_size","total"}}
//   Error:       {"detail": "..."} with a non-2xx HTTP status

import { API_BASE_URL } from '../utils/constants.js';

// Allows overriding the backend URL without editing source, e.g. from
// index.html: <script>window.SMART_CAMPUS_API_BASE_URL = 'http://host:8000/api';</script>
const BASE_URL = (typeof window !== 'undefined' && window.SMART_CAMPUS_API_BASE_URL) || API_BASE_URL;

let authToken = null;

export function setAuthToken(token) {
  authToken = token;
}

export function clearAuthToken() {
  authToken = null;
}

function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;
  return headers;
}

function buildUrl(path, params) {
  const url = new URL(`${BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, value);
      }
    });
  }
  return url.toString();
}

export async function apiRequest(path, { method = 'GET', body, params, headers } = {}) {
  let response;
  try {
    response = await fetch(buildUrl(path, params), {
      method,
      headers: buildHeaders(headers),
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    const error = new Error(`Cannot reach the backend at ${BASE_URL}. Is it running?`);
    error.code = 'NETWORK_ERROR';
    throw error;
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch { /* non-JSON error body */ }
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

export const apiClient = {
  get: (p, params) => apiRequest(p, { method: 'GET', params }),
  post: (p, body) => apiRequest(p, { method: 'POST', body }),
  patch: (p, body) => apiRequest(p, { method: 'PATCH', body }),
};

/** GETs a single-item endpoint and unwraps {"data": ...}. */
export async function getData(path, params) {
  const resp = await apiClient.get(path, params);
  return resp ? resp.data : null;
}

/** Follows the {data, pagination} envelope across every page (clamped to
 * the backend's page_size max of 100) and returns the combined list. */
export async function getAllPages(path, params = {}, pageSize = 100, hardCap = 2000) {
  const clampedSize = Math.min(pageSize, 100);
  let page = 1;
  const results = [];
  for (;;) {
    const resp = await apiClient.get(path, { ...params, page, page_size: clampedSize });
    const items = (resp && resp.data) || [];
    results.push(...items);
    const total = (resp && resp.pagination && resp.pagination.total) || results.length;
    if (!items.length || results.length >= total || results.length >= hardCap) break;
    page += 1;
  }
  return results;
}
