// ===== Gate pass service (Stage 2 — live backend) =====
//   submitGatePass()     -> POST /gatepasses
//   getMyGatePasses()    -> GET /gatepasses/my
//   getGatePassDetails() -> GET /gatepasses/{id}
//   cancelGatePass()     -> PATCH /gatepasses/{id}/cancel
//
// Note: the backend's GatePassCreate schema has no "remarks" field and
// rejects unknown fields outright (extra="forbid"), so the Stage 1 mock
// form's optional remarks box was removed from pages/GatePass.js.

import { apiClient, getAllPages, getData } from '../api/apiClient.js';

function toGatePass(row) {
  return {
    id: `GP${String(row.id).padStart(4, '0')}`,
    destination: row.destination,
    reason: row.reason,
    remarks: '',
    departureDate: row.departure_date,
    departureTime: row.departure_time,
    returnDate: row.return_date,
    returnTime: row.return_time,
    submittedAt: row.created_at,
    status: row.status,
    reviewedBy: row.hod_name,
    reviewRemarks: row.hod_remarks,
    reviewedAt: row.reviewed_at,
  };
}

function idToPk(id) {
  return parseInt(String(id).replace(/^GP/i, ''), 10);
}

export async function getMyGatePasses() {
  const rows = await getAllPages('/gatepasses/my');
  return rows.map(toGatePass).sort((a, b) => (a.submittedAt < b.submittedAt ? 1 : -1));
}

export async function getGatePassDetails(id) {
  const pk = idToPk(id);
  const row = await getData(`/gatepasses/${pk}`);
  if (!row) {
    const error = new Error('Gate pass not found.');
    error.code = 'NOT_FOUND';
    throw error;
  }
  return toGatePass(row);
}

/**
 * @param {Object} data { destination, reason, departureDate, departureTime, returnDate, returnTime }
 */
export async function submitGatePass(data) {
  const resp = await apiClient.post('/gatepasses', {
    destination: data.destination.trim(),
    reason: data.reason.trim(),
    departure_date: data.departureDate,
    departure_time: data.departureTime,
    return_date: data.returnDate,
    return_time: data.returnTime,
  });
  return toGatePass(resp.data);
}

export async function cancelGatePass(id) {
  const pk = idToPk(id);
  const resp = await apiClient.patch(`/gatepasses/${pk}/cancel`);
  return toGatePass(resp.data);
}

export async function getGatePassSummaryCounts() {
  const all = await getMyGatePasses();
  return {
    pending: all.filter((g) => g.status === 'PENDING').length,
    approved: all.filter((g) => g.status === 'APPROVED').length,
    rejected: all.filter((g) => g.status === 'REJECTED').length,
  };
}
