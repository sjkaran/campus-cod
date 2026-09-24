import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';

export function LoadingState(message = 'Loading…') {
  return h('div', { class: 'data-state' }, [
    h('div', { class: 'spinner' }),
    h('p', { class: 'data-state__text' }, message),
  ]);
}

export function EmptyState(message, iconName = 'inbox', actionEl = null) {
  return h('div', { class: 'data-state' }, [
    icon(iconName, { size: 32, class: 'data-state__icon' }),
    h('p', { class: 'data-state__text' }, message),
    actionEl,
  ]);
}

export function ErrorState(message, onRetry) {
  return h('div', { class: 'data-state data-state--error' }, [
    icon('warning', { size: 32, class: 'data-state__icon' }),
    h('p', { class: 'data-state__text' }, message || 'Something went wrong while loading this data.'),
    onRetry ? h('button', { class: 'btn btn--secondary btn--small', onClick: onRetry }, [icon('refresh', { size: 16 }), 'Retry']) : null,
  ]);
}
