// ===== Mock student data =====
// Stage 1 only. In Stage 2 this is replaced by GET /api/students/me.

export const MOCK_STUDENT = {
  id: 'STU-2026-001',
  name: 'Karan Mehta',
  rollNumber: 'CS26A014',
  department: 'Computer Science',
  semester: 6,
  section: 'A',
  email: 'karan.mehta@smartcampus.edu',
  phone: '+91 98765 43210',
  admissionYear: '2023',
};

// Mock credential store used only by the mock auth service.
export const MOCK_CREDENTIALS = {
  username: 'STU-2026-001',
  password: 'campus123',
};
