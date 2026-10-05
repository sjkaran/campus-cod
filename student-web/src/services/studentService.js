// ===== Student service (Stage 2 — live backend) =====
// getCurrentStudent() -> GET /students/me, department name resolved via
// GET /departments (cached — small, stable reference data).

import { getData } from '../api/apiClient.js';

let departmentsCache = null;

async function loadDepartments() {
  if (!departmentsCache) {
    departmentsCache = (await getData('/departments')) || [];
  }
  return departmentsCache;
}

async function nameForDepartmentCode(code) {
  const departments = await loadDepartments();
  const match = departments.find((d) => d.code === code);
  return match ? match.name : code || '—';
}

export async function getCurrentStudent() {
  const row = await getData('/students/me');
  return {
    id: row.student_id,
    name: row.name,
    rollNumber: row.roll_number,
    department: await nameForDepartmentCode(row.department_code),
    semester: row.semester,
    section: row.section,
    email: row.email,
    phone: row.phone || '',
    admissionYear: '', // not modeled by the backend yet
  };
}
