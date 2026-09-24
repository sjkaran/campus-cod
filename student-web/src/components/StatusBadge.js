import { h } from '../utils/dom.js';

const VARIANTS = {
  PENDING: 'badge--pending',
  APPROVED: 'badge--approved',
  REJECTED: 'badge--rejected',
  Present: 'badge--approved',
  Absent: 'badge--rejected',
  high: 'badge--rejected',
  normal: 'badge--pending',
  low: 'badge--neutral',
};

export function StatusBadge(label, variantKey) {
  const cls = VARIANTS[variantKey] || 'badge--neutral';
  return h('span', { class: `badge ${cls}` }, label);
}
