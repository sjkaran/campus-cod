// ===== Notification service (Stage 2 — live backend) =====
//   getNotifications()       -> GET /notifications (targeted at me)
//   markNotificationAsRead() -> PATCH /notifications/{id}/read
//
// Backend priority is NORMAL/IMPORTANT/URGENT (3 levels); the UI only
// visually distinguishes "high" from everything else, so IMPORTANT and
// URGENT both map to 'high' and NORMAL maps to 'normal'.

import { apiClient, getAllPages } from '../api/apiClient.js';

const AUDIENCE_LABELS = {
  ALL_STUDENTS: 'All Students',
  DEPARTMENT: 'Department',
  SEMESTER: 'Semester',
  SECTION: 'Section',
};

function mapPriority(backendPriority) {
  return backendPriority === 'NORMAL' ? 'normal' : 'high';
}

function toNotification(row) {
  return {
    id: row.id,
    title: row.title,
    message: row.message,
    publisher: row.author_name || '—',
    audience: AUDIENCE_LABELS[row.audience_type] || row.audience_type,
    priority: mapPriority(row.priority),
    createdAt: row.created_at,
    read: Boolean(row.is_read),
  };
}

export async function getNotifications() {
  const rows = await getAllPages('/notifications');
  return rows.map(toNotification).sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
}

export async function markNotificationAsRead(id) {
  const resp = await apiClient.patch(`/notifications/${id}/read`);
  return resp.data;
}

export async function getUnreadCount() {
  const all = await getNotifications();
  return all.filter((n) => !n.read).length;
}
