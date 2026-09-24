// ===== Notification service =====
// Stage 1: mock/notifications.js (mutated in-memory for read/unread state)
// Stage 2:
//   getNotifications()      -> GET /api/notifications
//   markNotificationAsRead() -> PATCH /api/notifications/{id}/read

import { MOCK_NOTIFICATIONS } from '../mock/notifications.js';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getNotifications() {
  await delay(400);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/notifications');
  return [...MOCK_NOTIFICATIONS].sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
}

export async function markNotificationAsRead(id) {
  await delay(150);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.patch(`/notifications/${id}/read`);
  const target = MOCK_NOTIFICATIONS.find((n) => n.id === id);
  if (target) target.read = true;
  return target ? { ...target } : null;
}

export async function getUnreadCount() {
  const all = await getNotifications();
  return all.filter((n) => !n.read).length;
}
