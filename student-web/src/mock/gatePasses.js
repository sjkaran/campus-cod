// ===== Mock gate pass data =====
// Stage 1 only. This module holds an in-memory, mutable list so the
// prototype can simulate submitting new requests within a session.
// In Stage 2 this is replaced by POST /api/gatepasses and
// GET /api/gatepasses/my.

export const MOCK_GATE_PASSES = [
  {
    id: 'GP001',
    destination: 'Home (Bhubaneswar)',
    reason: 'Family function over the weekend, requesting leave to travel home.',
    remarks: '',
    departureDate: '2026-09-19',
    departureTime: '16:00',
    returnDate: '2026-09-21',
    returnTime: '20:00',
    submittedAt: '2026-09-17T10:12:00',
    status: 'APPROVED',
    reviewedBy: 'Dr. A. Sharma (HOD, CSE)',
    reviewRemarks: 'Approved. Please carry your ID card while travelling.',
    reviewedAt: '2026-09-17T15:30:00',
  },
  {
    id: 'GP002',
    destination: 'City Hospital',
    reason: 'Medical appointment for a follow-up consultation.',
    remarks: 'Will return same evening.',
    departureDate: '2026-09-14',
    departureTime: '09:00',
    returnDate: '2026-09-14',
    returnTime: '13:00',
    submittedAt: '2026-09-13T08:05:00',
    status: 'REJECTED',
    reviewedBy: 'Dr. A. Sharma (HOD, CSE)',
    reviewRemarks: 'Insufficient information provided. Please attach appointment details and resubmit.',
    reviewedAt: '2026-09-13T18:45:00',
  },
  {
    id: 'GP003',
    destination: 'Railway Station',
    reason: 'Picking up a family member arriving by train.',
    remarks: '',
    departureDate: '2026-09-24',
    departureTime: '17:30',
    returnDate: '2026-09-24',
    returnTime: '21:00',
    submittedAt: '2026-09-22T19:20:00',
    status: 'PENDING',
    reviewedBy: null,
    reviewRemarks: null,
    reviewedAt: null,
  },
];

let nextId = 4;
export function generateGatePassId() {
  const id = `GP${String(nextId).padStart(3, '0')}`;
  nextId += 1;
  return id;
}
