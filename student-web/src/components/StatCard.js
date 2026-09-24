import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';

/**
 * @param {Object} opts
 * @param {string} opts.label
 * @param {string} opts.value
 * @param {string} [opts.meta]
 * @param {string} [opts.iconName]
 * @param {'neutral'|'good'|'warning'|'bad'} [opts.tone]
 */
export function StatCard({ label, value, meta, iconName, tone = 'neutral' }) {
  return h('div', { class: `stat-card stat-card--${tone}` }, [
    h('div', { class: 'stat-card__top' }, [
      h('span', { class: 'stat-card__label' }, label),
      iconName ? icon(iconName, { class: 'stat-card__icon' }) : null,
    ]),
    h('div', { class: 'stat-card__value' }, value),
    meta ? h('div', { class: 'stat-card__meta' }, meta) : null,
  ]);
}
