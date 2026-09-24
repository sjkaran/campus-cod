// REAL implementation (Stage 2). Must return the same shapes as mockService.js.
import { http } from './apiClient.js';

export const apiService = {
  login: (studentId, password) => http('POST', '/auth/login', { studentId, password }), // -> { token, student }
  getProfile: () => http('GET', '/students/me'),
  getNotifications: () => http('GET', '/notifications'),
  getAttendance: () => http('GET', '/students/me/attendance'), // -> { minRequired, overall, subjects[] }
  getGatePasses: () => http('GET', '/students/me/gate-passes'),
  submitGatePass: (payload) => http('POST', '/gate-passes', payload),
};
