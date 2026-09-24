import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';

let container = null;

function getContainer() {
  if (!container) {
    container = document.getElementById('toast-root');
  }
  return container;
}

/**
 * @param {string} message
 * @param {'success'|'error'|'info'} [type]
 */
export function showToast(message, type = 'success') {
  const root = getContainer();
  if (!root) return;
  const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'warning' : 'bell';
  const toast = h('div', { class: `toast toast--${type}` }, [
    icon(iconName, { size: 18 }),
    h('span', {}, message),
  ]);
  root.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('toast--visible'));
  setTimeout(() => {
    toast.classList.remove('toast--visible');
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}
