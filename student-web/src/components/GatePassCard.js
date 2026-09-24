import { h } from '../utils/dom.js';
import { formatDate, formatDateTime } from '../utils/formatting.js';
import { StatusBadge } from './StatusBadge.js';

/**
 * @param {import('../models/models.js').GatePass} gp
 * @param {(id: string) => void} onOpen
 */
export function GatePassCard(gp, onOpen) {
  return h('article', { class: 'gatepass-card', onClick: () => onOpen(gp.id), role: 'button', tabindex: '0' }, [
    h('div', { class: 'gatepass-card__head' }, [
      h('div', {}, [
        h('span', { class: 'gatepass-card__id' }, gp.id),
        h('h3', { class: 'gatepass-card__destination' }, gp.destination),
      ]),
      StatusBadge(gp.status, gp.status),
    ]),
    h('p', { class: 'gatepass-card__reason' }, gp.reason),
    h('div', { class: 'gatepass-card__grid' }, [
      h('div', {}, [h('span', { class: 'field-label' }, 'Departure'), h('span', {}, `${formatDate(gp.departureDate)} · ${gp.departureTime}`)]),
      h('div', {}, [h('span', { class: 'field-label' }, 'Return'), h('span', {}, `${formatDate(gp.returnDate)} · ${gp.returnTime}`)]),
      h('div', {}, [h('span', { class: 'field-label' }, 'Submitted'), h('span', {}, formatDateTime(gp.submittedAt))]),
    ]),
    gp.status === 'REJECTED' && gp.reviewRemarks
      ? h('p', { class: 'gatepass-card__rejection' }, [h('strong', {}, 'Reason: '), gp.reviewRemarks])
      : null,
  ]);
}
