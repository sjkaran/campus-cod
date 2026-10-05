// ===== Attendance service (Stage 2 — live backend) =====
//   getAttendanceSummary()  -> GET /students/me/attendance (overall)
//   getSubjectAttendance()  -> GET /students/me/attendance (subjects)
//   getAttendanceHistory()  -> NOT YET AVAILABLE server-side. The backend
//     only exposes per-session attendance detail to FACULTY/HOD/ADMIN
//     (GET /attendance/sessions/{id}), not to the student who was marked.
//     This always resolves to [] until that endpoint exists — the
//     Attendance page shows an explanatory note rather than faking records.

import { getData } from '../api/apiClient.js';
import { APP_CONFIG } from '../utils/constants.js';

export async function getAttendanceSummary() {
  const data = await getData('/students/me/attendance');
  const overall = data.overall;
  return {
    totalClasses: overall.total_classes,
    present: overall.present,
    absent: overall.absent,
    percentage: overall.percentage,
    threshold: APP_CONFIG.ATTENDANCE_WARNING_THRESHOLD,
  };
}

export async function getSubjectAttendance() {
  const data = await getData('/students/me/attendance');
  return data.subjects.map((s) => ({
    subject: s.subject_name,
    totalClasses: s.total_classes,
    present: s.present,
    absent: s.absent,
    percentage: s.percentage,
  }));
}

export async function getAttendanceHistory(_filters = {}) {
  return [];
}

export const ATTENDANCE_HISTORY_UNAVAILABLE =
  'Day-by-day attendance history isn\u2019t available from the backend yet — only the subject-wise totals above are. ' +
  'This will populate automatically once a student-facing session history endpoint is added.';
