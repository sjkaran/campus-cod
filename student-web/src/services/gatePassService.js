// ===== Gate pass service =====
// Stage 1: mock/gatePasses.js (mutable in-memory list)
// Stage 2:
//   submitGatePass()   -> POST /api/gatepasses
//   getMyGatePasses()  -> GET /api/gatepasses/my
//   getGatePassDetails() -> GET /api/gatepasses/{id}

import { MOCK_GATE_PASSES, generateGatePassId } from '../mock/gatePasses.js';
import { GATE_PASS_STATUS } from '../utils/constants.js';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getMyGatePasses() {
  await delay(400);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/gatepasses/my');
  return [...MOCK_GATE_PASSES].sort((a, b) => (a.submittedAt < b.submittedAt ? 1 : -1));
}

export async function getGatePassDetails(id) {
  await delay(300);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get(`/gatepasses/${id}`);
  const found = MOCK_GATE_PASSES.find((gp) => gp.id === id);
  if (!found) {
    const error = new Error('Gate pass not found.');
    error.code = 'NOT_FOUND';
    throw error;
  }
  return { ...found };
}

/**
 * @param {Object} data
 * @returns {Promise<Object>} the created gate pass
 */
export async function submitGatePass(data) {
  await delay(600);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.post('/gatepasses', data);
  const record = {
    id: generateGatePassId(),
    destination: data.destination.trim(),
    reason: data.reason.trim(),
    remarks: (data.remarks || '').trim(),
    departureDate: data.departureDate,
    departureTime: data.departureTime,
    returnDate: data.returnDate,
    returnTime: data.returnTime,
    submittedAt: new Date().toISOString(),
    status: GATE_PASS_STATUS.PENDING,
    reviewedBy: null,
    reviewRemarks: null,
    reviewedAt: null,
  };
  MOCK_GATE_PASSES.unshift(record);
  return { ...record };
}

export async function getGatePassSummaryCounts() {
  const all = await getMyGatePasses();
  return {
    pending: all.filter((g) => g.status === GATE_PASS_STATUS.PENDING).length,
    approved: all.filter((g) => g.status === GATE_PASS_STATUS.APPROVED).length,
    rejected: all.filter((g) => g.status === GATE_PASS_STATUS.REJECTED).length,
  };
}
