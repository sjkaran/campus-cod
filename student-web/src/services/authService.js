// ===== Auth service (Stage 2 — live backend) =====
// UI calls loginStudent()/logoutStudent()/getSession() only. Nothing else
// in the app knows whether it's talking to mock data or the real API.

import { apiClient, setAuthToken, clearAuthToken } from '../api/apiClient.js';
import { SESSION_KEY } from '../utils/constants.js';

export async function loginStudent(username, password) {
  const response = await apiClient.post('/auth/login', {
    username: username.trim(),
    password,
  });
  // response: { access_token, token_type, expires_in, user: { id, username, role, name, department_code } }

  if (response.user.role !== 'STUDENT') {
    const error = new Error(
      `This portal is for Student accounts only. That login has the ${response.user.role} role.`,
    );
    error.code = 'WRONG_ROLE';
    throw error;
  }

  const session = {
    token: response.access_token,
    username: response.user.username,
    issuedAt: new Date().toISOString(),
  };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  setAuthToken(session.token);
  return session;
}

export function logoutStudent() {
  sessionStorage.removeItem(SESSION_KEY);
  clearAuthToken();
}

export function getSession() {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    const session = JSON.parse(raw);
    setAuthToken(session.token); // re-attach token for this page load
    return session;
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getSession());
}
