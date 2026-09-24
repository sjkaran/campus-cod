import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { getNotifications, markNotificationAsRead } from '../services/notificationService.js';
import { NotificationCard } from '../components/NotificationCard.js';
import { LoadingState, ErrorState, EmptyState } from '../components/DataState.js';

export function NotificationsPage() {
  const state = { all: [], filter: 'all', query: '', status: 'loading' };
  const root = h('div', { class: 'page' });

  const toolbar = h('div', { class: 'toolbar' }, [
    h('div', { class: 'search-input' }, [
      icon('search', { size: 16 }),
      h('input', {
        type: 'text', placeholder: 'Search notifications…',
        onInput: (e) => { state.query = e.target.value.toLowerCase(); renderList(); },
      }),
    ]),
    h('div', { class: 'segmented' }, [
      segmentButton('all', 'All'),
      segmentButton('unread', 'Unread'),
      segmentButton('high', 'High priority'),
    ]),
  ]);

  const listSlot = h('div', {});
  root.append(h('div', { class: 'page__head' }, h('h2', { class: 'page__title' }, 'Notifications')), toolbar, listSlot);

  function segmentButton(value, label) {
    return h('button', {
      class: `segmented__btn ${state.filter === value ? 'segmented__btn--active' : ''}`,
      onClick: () => { state.filter = value; renderList(); refreshSegmentClasses(); },
    }, label);
  }

  function refreshSegmentClasses() {
    toolbar.querySelectorAll('.segmented__btn').forEach((btn, idx) => {
      const values = ['all', 'unread', 'high'];
      btn.classList.toggle('segmented__btn--active', values[idx] === state.filter);
    });
  }

  function getFiltered() {
    return state.all.filter((n) => {
      if (state.filter === 'unread' && n.read) return false;
      if (state.filter === 'high' && n.priority !== 'high') return false;
      if (state.query && !`${n.title} ${n.message}`.toLowerCase().includes(state.query)) return false;
      return true;
    });
  }

  function renderList() {
    if (state.status === 'loading') { listSlot.replaceChildren(LoadingState('Loading notifications…')); return; }
    if (state.status === 'error') { listSlot.replaceChildren(ErrorState('Unable to load notifications. Please try again.', load)); return; }
    const filtered = getFiltered();
    if (!filtered.length) { listSlot.replaceChildren(EmptyState('No new notifications.', 'inbox')); return; }
    listSlot.replaceChildren(h('div', { class: 'notification-list' }, filtered.map((n) => NotificationCard(n, handleMarkRead))));
  }

  async function load() {
    state.status = 'loading';
    renderList();
    try {
      state.all = await getNotifications();
      state.status = 'success';
    } catch {
      state.status = 'error';
    }
    renderList();
  }

  async function handleMarkRead(id) {
    await markNotificationAsRead(id);
    const target = state.all.find((n) => n.id === id);
    if (target) target.read = true;
    renderList();
  }

  load();
  return root;
}
