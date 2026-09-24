// ===== Auth service =====
// UI calls loginStudent()/logoutStudent()/getSession() only. Nothing else
// in the app knows whether it's talking to mock data or a real API.
//
// Stage 1:  loginStudent() -> MockAuthService
// Stage 2:  loginStudent() -> ApiAuthService -> POST /api/auth/login

import { MOCK_CREDENTIALS } from '../mock/students.js';
import { SESSION_KEY } from '../utils/constants.js';

const ARTIFICIAL_DELAY_MS = 500;

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Attempts to authenticate a student.
 * @returns {Promise<{ token: string }>}
 */
export async function loginStudent(username, password) {
  await delay(ARTIFICIAL_DELAY_MS);

  // ----- FUTURE API INTEGRATION -----
  // Replace this mock check with:
  //   const { token } = await apiClient.post('/auth/login', { username, password });
  const valid = username.trim() === MOCK_CREDENTIALS.username
    && password === MOCK_CREDENTIALS.password;

  if (!valid) {
    const error = new Error('Invalid Student ID or password.');
    error.code = 'INVALID_CREDENTIALS';
    throw error;
  }

  const session = {
    token: `mock-token.${btoa(username)}.${Date.now()}`,
    username,
    issuedAt: new Date().toISOString(),
  };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export function logoutStudent() {
  sessionStorage.removeItem(SESSION_KEY);
}

export function getSession() {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getSession());
}
