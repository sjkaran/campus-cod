// ===== Mock attendance data =====
// Stage 1 only. In Stage 2 this is replaced by:
//   GET /api/students/me/attendance
//   GET /api/students/me/attendance/subjects
//   GET /api/students/me/attendance/history

export const MOCK_SUBJECT_ATTENDANCE = [
  { subject: 'Artificial Intelligence', totalClasses: 40, present: 35, absent: 5 },
  { subject: 'Database Systems', totalClasses: 38, present: 31, absent: 7 },
  { subject: 'Operating Systems', totalClasses: 42, present: 36, absent: 6 },
  { subject: 'Computer Networks', totalClasses: 36, present: 24, absent: 12 },
  { subject: 'Software Engineering', totalClasses: 30, present: 28, absent: 2 },
].map((s) => ({ ...s, percentage: Number(((s.present / s.totalClasses) * 100).toFixed(1)) }));

const SESSIONS = ['Morning', 'Afternoon'];
const SUBJECTS = MOCK_SUBJECT_ATTENDANCE.map((s) => s.subject);

function buildHistory() {
  const records = [];
  const start = new Date('2026-09-23');
  let day = 0;
  // Generate ~45 days of records across subjects, skipping Sundays.
  for (let i = 0; records.length < 90 && i < 65; i += 1) {
    const date = new Date(start);
    date.setDate(start.getDate() - i);
    if (date.getDay() === 0) continue; // skip Sunday
    day += 1;
    SUBJECTS.forEach((subject, idx) => {
      if ((day + idx) % 3 === 0) return; // not every subject meets every day
      const session = SESSIONS[(day + idx) % SESSIONS.length];
      // Deterministic pseudo-random attendance leaning "present".
      const seed = (day * 7 + idx * 13) % 10;
      const status = seed < 8 ? 'Present' : 'Absent';
      records.push({
        date: date.toISOString().slice(0, 10),
        subject,
        session,
        status,
      });
    });
  }
  return records.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export const MOCK_ATTENDANCE_HISTORY = buildHistory();
