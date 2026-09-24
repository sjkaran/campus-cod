// ===== Attendance service =====
// Stage 1: mock/attendance.js
// Stage 2:
//   getAttendanceSummary()  -> GET /api/students/me/attendance
//   getSubjectAttendance()  -> GET /api/students/me/attendance/subjects
//   getAttendanceHistory()  -> GET /api/students/me/attendance/history

import { MOCK_SUBJECT_ATTENDANCE, MOCK_ATTENDANCE_HISTORY } from '../mock/attendance.js';
import { APP_CONFIG } from '../utils/constants.js';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getAttendanceSummary() {
  await delay(350);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/students/me/attendance');
  const totalClasses = MOCK_SUBJECT_ATTENDANCE.reduce((sum, s) => sum + s.totalClasses, 0);
  const present = MOCK_SUBJECT_ATTENDANCE.reduce((sum, s) => sum + s.present, 0);
  const absent = totalClasses - present;
  const percentage = totalClasses ? Number(((present / totalClasses) * 100).toFixed(1)) : 0;
  return { totalClasses, present, absent, percentage, threshold: APP_CONFIG.ATTENDANCE_WARNING_THRESHOLD };
}

export async function getSubjectAttendance() {
  await delay(400);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/students/me/attendance/subjects');
  return [...MOCK_SUBJECT_ATTENDANCE];
}

/**
 * @param {Object} filters
 * @param {string} [filters.subject]
 * @param {string} [filters.status]
 * @param {string} [filters.fromDate]
 * @param {string} [filters.toDate]
 */
export async function getAttendanceHistory(filters = {}) {
  await delay(400);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/students/me/attendance/history', { params: filters });
  return MOCK_ATTENDANCE_HISTORY.filter((record) => {
    if (filters.subject && filters.subject !== 'all' && record.subject !== filters.subject) return false;
    if (filters.status && filters.status !== 'all' && record.status !== filters.status) return false;
    if (filters.fromDate && record.date < filters.fromDate) return false;
    if (filters.toDate && record.date > filters.toDate) return false;
    return true;
  });
}
