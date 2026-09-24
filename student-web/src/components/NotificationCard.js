import { h } from '../utils/dom.js';
import { formatDateTime, formatRelativeTime } from '../utils/formatting.js';
import { StatusBadge } from './StatusBadge.js';

/**
 * @param {import('../models/models.js').Notification} note
 * @param {(id: string) => void} onMarkRead
 * @param {boolean} [compact] use relative time + tighter layout (dashboard)
 */
export function NotificationCard(note, onMarkRead, compact = false) {
  const card = h('article', { class: `notification-card ${note.read ? '' : 'notification-card--unread'}` }, [
    h('div', { class: 'notification-card__head' }, [
      h('div', { class: 'notification-card__title-row' }, [
        !note.read ? h('span', { class: 'unread-dot', 'aria-label': 'Unread' }) : null,
        h('h3', { class: 'notification-card__title' }, note.title),
      ]),
      note.priority === 'high' ? StatusBadge('High priority', 'high') : null,
    ]),
    h('p', { class: 'notification-card__meta' }, `${note.publisher} · ${note.audience}`),
    h('p', { class: 'notification-card__message' }, note.message),
    h('div', { class: 'notification-card__foot' }, [
      h('span', { class: 'notification-card__date' }, compact ? formatRelativeTime(note.createdAt) : formatDateTime(note.createdAt)),
      !note.read && onMarkRead
        ? h('button', { class: 'btn btn--ghost btn--small', onClick: () => onMarkRead(note.id) }, 'Mark as read')
        : null,
    ]),
  ]);
  return card;
}
