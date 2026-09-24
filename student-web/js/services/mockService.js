// MOCK implementation (Stage 1). Every method notes the endpoint that replaces it.
import { CONFIG } from '../config.js';
import { MOCK_STUDENT, MOCK_PASSWORD, MOCK_NOTIFICATIONS, MOCK_ATTENDANCE, MOCK_GATE_PASSES } from '../data/mockData.js';

const wait = () => new Promise((r) => setTimeout(r, CONFIG.MOCK_LATENCY_MS));
const gatePasses = structuredClone(MOCK_GATE_PASSES);
const pct = (a, t) => Math.round((a / t) * 1000) / 10;

export const mockService = {
  // POST /api/auth/login
  async login(studentId, password) {
    await wait();
    if (studentId.trim().toUpperCase() !== MOCK_STUDENT.id || password !== MOCK_PASSWORD) throw new Error('Student ID or password is incorrect.');
    return { token: 'mock-token', student: MOCK_STUDENT };
  },
  // GET /api/students/me
  async getProfile() { await wait(); return MOCK_STUDENT; },
  // GET /api/notifications
  async getNotifications() { await wait(); return [...MOCK_NOTIFICATIONS].sort((a, b) => b.date.localeCompare(a.date)); },
  // GET /api/students/me/attendance  (backend computes percentages and the minimum threshold)
  async getAttendance() {
    await wait();
    const subjects = MOCK_ATTENDANCE.map((s) => ({ ...s, percentage: pct(s.attended, s.total) }));
    const att = subjects.reduce((n, s) => n + s.attended, 0), tot = subjects.reduce((n, s) => n + s.total, 0);
    return { minRequired: 75, overall: pct(att, tot), subjects };
  },
  // GET /api/students/me/gate-passes
  async getGatePasses() { await wait(); return [...gatePasses]; },
  // POST /api/gate-passes  (backend re-validates everything; new requests always start PENDING)
  async submitGatePass(p) {
    await wait();
    const gp = { id: `GP-${1000 + gatePasses.length + 1}`, appliedOn: new Date().toISOString().slice(0, 10), status: 'PENDING', remarks: '', ...p };
    gatePasses.unshift(gp);
    return gp;
  },
};
