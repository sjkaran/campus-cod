// ===== Application-wide constants =====
// Centralising these avoids magic strings scattered across the UI, and
// keeps route/status vocabulary in one place so it stays in sync with the
// eventual backend contract.

export const ROUTES = {
  LOGIN: 'login',
  DASHBOARD: 'dashboard',
  NOTIFICATIONS: 'notifications',
  ATTENDANCE: 'attendance',
  GATEPASS: 'gatepass',
  GATEPASS_DETAILS: 'gatepass-details',
  PROFILE: 'profile',
};

export const NAV_ITEMS = [
  { route: ROUTES.DASHBOARD, label: 'Dashboard', icon: 'grid' },
  { route: ROUTES.NOTIFICATIONS, label: 'Notifications', icon: 'bell' },
  { route: ROUTES.ATTENDANCE, label: 'Attendance', icon: 'check-circle' },
  { route: ROUTES.GATEPASS, label: 'Gate Pass', icon: 'door' },
  { route: ROUTES.PROFILE, label: 'Profile', icon: 'user' },
];

export const GATE_PASS_STATUS = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
};

export const ATTENDANCE_STATUS = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
};

export const NOTIFICATION_PRIORITY = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
};

// Stage 1 mock config. In Stage 2 this will be delivered by the backend
// (e.g. GET /api/config) rather than hard-coded on the client.
export const APP_CONFIG = {
  ATTENDANCE_WARNING_THRESHOLD: 75,
};

export const SESSION_KEY = 'sc_student_session';
