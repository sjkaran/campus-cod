import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';

/**
 * @param {Object} opts
 * @param {string} opts.title
 * @param {HTMLElement|string} opts.body
 * @param {{label:string, variant?:string, onClick:Function}[]} opts.actions
 * @returns {{ el: HTMLElement, close: Function }}
 */
export function openModal({ title, body, actions = [] }) {
  const backdrop = h('div', { class: 'modal-backdrop' });
  const close = () => {
    backdrop.classList.remove('modal-backdrop--visible');
    setTimeout(() => backdrop.remove(), 150);
  };

  const dialog = h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true' }, [
    h('div', { class: 'modal__head' }, [
      h('h2', { class: 'modal__title' }, title),
      h('button', { class: 'icon-button', onClick: close, 'aria-label': 'Close' }, icon('close', { size: 18 })),
    ]),
    h('div', { class: 'modal__body' }, body),
    actions.length
      ? h('div', { class: 'modal__actions' }, actions.map((a) => h('button', {
        class: `btn ${a.variant === 'primary' ? 'btn--primary' : 'btn--secondary'}`,
        onClick: () => a.onClick(close),
      }, a.label)))
      : null,
  ]);

  backdrop.appendChild(dialog);
  backdrop.addEventListener('click', (e) => { if (e.target === backdrop) close(); });
  document.body.appendChild(backdrop);
  requestAnimationFrame(() => backdrop.classList.add('modal-backdrop--visible'));

  return { el: backdrop, close };
}
