import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { getGatePassDetails, cancelGatePass } from '../services/gatePassService.js';
import { formatDate, formatDateTime } from '../utils/formatting.js';
import { StatusBadge } from '../components/StatusBadge.js';
import { LoadingState, ErrorState } from '../components/DataState.js';
import { openModal } from '../components/Modal.js';
import { showToast } from '../components/Toast.js';

/**
 * @param {string} id
 * @param {import('../models/models.js').Student} student
 * @param {()=>void} onBack
 */
export function GatePassDetailsPage(id, student, onBack) {
  const root = h('div', { class: 'page' });
  const slot = h('div', { class: 'panel' }, LoadingState('Loading gate pass details…'));

  root.append(
    h('button', { class: 'btn btn--ghost btn--small back-link', onClick: onBack }, [icon('arrowLeft', { size: 16 }), 'Back to Gate Pass']),
    slot,
  );

  function timeline(status) {
    const steps = status === 'REJECTED'
      ? [{ label: 'Submitted', done: true }, { label: 'Under Review', done: true }, { label: 'Rejected', done: true, bad: true }]
      : status === 'APPROVED'
        ? [{ label: 'Submitted', done: true }, { label: 'Under Review', done: true }, { label: 'Approved', done: true }]
        : status === 'CANCELLED'
          ? [{ label: 'Submitted', done: true }, { label: 'Cancelled', done: true, bad: true }]
          : [{ label: 'Submitted', done: true }, { label: 'Under Review', done: true, current: true }, { label: 'Decision', done: false }];

    return h('div', { class: 'timeline' }, steps.map((s, idx) => h('div', { class: `timeline__step ${s.done ? 'timeline__step--done' : ''} ${s.bad ? 'timeline__step--bad' : ''} ${s.current ? 'timeline__step--current' : ''}` }, [
      h('span', { class: 'timeline__dot' }),
      h('span', { class: 'timeline__label' }, s.label),
      idx < steps.length - 1 ? h('span', { class: 'timeline__connector' }) : null,
    ])));
  }

  function handleCancel(gp) {
    openModal({
      title: 'Cancel gate pass',
      body: 'Are you sure you want to cancel this gate-pass request? This cannot be undone.',
      actions: [
        { label: 'Keep it', variant: 'secondary', onClick: (close) => close() },
        {
          label: 'Cancel Request', variant: 'primary',
          onClick: async (close) => {
            close();
            try {
              await cancelGatePass(gp.id);
              showToast('Gate-pass request cancelled.', 'success');
              load();
            } catch (err) {
              showToast(err.message || 'Unable to cancel this request.', 'error');
            }
          },
        },
      ],
    });
  }

  async function load() {
    try {
      const gp = await getGatePassDetails(id);
      slot.replaceChildren(
        h('div', { class: 'panel__head' }, [
          h('div', {}, [
            h('span', { class: 'gatepass-card__id' }, gp.id),
            h('h3', { class: 'panel__title' }, gp.destination),
          ]),
          h('div', {}, [
            StatusBadge(gp.status, gp.status),
            gp.status === 'PENDING'
              ? h('button', { class: 'btn btn--ghost btn--small', style: 'margin-left:8px', onClick: () => handleCancel(gp) }, 'Cancel Request')
              : null,
          ]),
        ]),
        timeline(gp.status),
        h('div', { class: 'details-grid' }, [
          h('div', {}, [h('span', { class: 'field-label' }, 'Student'), h('p', {}, `${student.name} (${student.rollNumber})`)]),
          h('div', {}, [h('span', { class: 'field-label' }, 'Reason'), h('p', {}, gp.reason)]),
          h('div', {}, [h('span', { class: 'field-label' }, 'Departure'), h('p', {}, `${formatDate(gp.departureDate)} · ${gp.departureTime}`)]),
          h('div', {}, [h('span', { class: 'field-label' }, 'Expected return'), h('p', {}, `${formatDate(gp.returnDate)} · ${gp.returnTime}`)]),
          h('div', {}, [h('span', { class: 'field-label' }, 'Submitted'), h('p', {}, formatDateTime(gp.submittedAt))]),
          gp.remarks ? h('div', {}, [h('span', { class: 'field-label' }, 'Remarks'), h('p', {}, gp.remarks)]) : null,
        ]),
        gp.status !== 'PENDING'
          ? h('div', { class: `review-box ${gp.status === 'REJECTED' ? 'review-box--rejected' : 'review-box--approved'}` }, [
            h('p', { class: 'field-label' }, gp.status === 'REJECTED' ? 'Rejection remarks' : 'Approval remarks'),
            h('p', {}, gp.reviewRemarks || '—'),
            h('p', { class: 'review-box__meta' }, `${gp.reviewedBy || 'Reviewer'} · ${formatDateTime(gp.reviewedAt)}`),
          ])
          : null,
      );
    } catch {
      slot.replaceChildren(ErrorState('Unable to load gate pass details. Please try again.', load));
    }
  }

  load();
  return root;
}
