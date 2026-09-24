// MOCK DATA ONLY. Consumed exclusively by services/mockService.js.
export const MOCK_PASSWORD = 'student123';
export const MOCK_STUDENT = {
  id: 'S2021045', name: 'Aarav Sharma', email: 'aarav.sharma@campus.edu', phone: '+91 98200 12345',
  department: 'Computer Engineering', year: 'Third Year', division: 'A', rollNo: 45, hod: 'Dr. R. Kulkarni',
};
export const MOCK_NOTIFICATIONS = [
  { id: 1, title: 'Mid-semester exam timetable published', body: 'Exams begin on 6 October. The full timetable is on the department notice board.', category: 'Academic', source: 'Admin Office', date: '2026-09-22' },
  { id: 2, title: 'Library closed on Saturday', body: 'The central library will be closed on 26 September for stock verification.', category: 'General', source: 'Admin Office', date: '2026-09-20' },
  { id: 3, title: 'Project review schedule', body: 'Third-year project reviews run from 1 to 3 October. Groups will be told their slots by email.', category: 'Academic', source: 'HOD, Computer Engineering', date: '2026-09-18' },
  { id: 4, title: 'Tech fest volunteers needed', body: 'Register with the student council by 28 September to volunteer for Technova.', category: 'Events', source: 'Admin Office', date: '2026-09-15' },
];
export const MOCK_ATTENDANCE = [
  { code: 'CS301', subject: 'Operating Systems', faculty: 'Prof. M. Iyer', attended: 34, total: 40 },
  { code: 'CS302', subject: 'Database Management', faculty: 'Dr. S. Nair', attended: 30, total: 38 },
  { code: 'CS303', subject: 'Computer Networks', faculty: 'Prof. A. Deshmukh', attended: 26, total: 40 },
  { code: 'CS304', subject: 'Software Engineering', faculty: 'Dr. P. Joshi', attended: 29, total: 36 },
  { code: 'CS305', subject: 'Theory of Computation', faculty: 'Prof. K. Rao', attended: 31, total: 35 },
];
export const MOCK_GATE_PASSES = [
  { id: 'GP-1003', appliedOn: '2026-09-21', outDate: '2026-09-25', outTime: '14:00', returnTime: '18:00', destination: 'City Hospital', reason: 'Dental appointment', status: 'PENDING', remarks: '' },
  { id: 'GP-1002', appliedOn: '2026-09-10', outDate: '2026-09-12', outTime: '11:00', returnTime: '16:00', destination: 'Passport Office', reason: 'Passport verification', status: 'APPROVED', remarks: '' },
  { id: 'GP-1001', appliedOn: '2026-09-03', outDate: '2026-09-05', outTime: '09:00', returnTime: '17:00', destination: 'Home', reason: 'Family function', status: 'REJECTED', remarks: 'Lab practical scheduled that day. Reapply for another date.' },
];
