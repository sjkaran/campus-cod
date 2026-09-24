import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { validateGatePassForm } from '../utils/validation.js';
import { submitGatePass, getMyGatePasses } from '../services/gatePassService.js';
import { GatePassCard } from '../components/GatePassCard.js';
import { LoadingState, ErrorState, EmptyState } from '../components/DataState.js';
import { openModal } from '../components/Modal.js';
import { showToast } from '../components/Toast.js';
import { formatDate } from '../utils/formatting.js';

/** @param {(id:string)=>void} onOpenDetails */
export function GatePassPage(onOpenDetails) {
  const form = { destination: '', reason: '', remarks: '', departureDate: '', departureTime: '', returnDate: '', returnTime: '' };
  let errors = {};
  let submitting = false;
  const historyState = { items: [], status: 'loading' };

  const root = h('div', { class: 'page' });

  const formSlot = h('form', { class: 'gatepass-form', onSubmit: handleSubmit });
  const historySlot = h('div', {});

  root.append(
    h('div', { class: 'page__head' }, h('h2', { class: 'page__title' }, 'Gate Pass')),
    h('div', { class: 'gatepass-layout' }, [
      h('section', { class: 'panel' }, [
        h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Apply for Gate Pass')),
        formSlot,
      ]),
      h('section', { class: 'panel' }, [
        h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Gate Pass History')),
        historySlot,
      ]),
    ]),
  );

  function field(key, label, opts = {}) {
    const errorMsg = errors[key];
    const input = opts.textarea
      ? h('textarea', {
        class: `field-input field-textarea ${errorMsg ? 'field-input--error' : ''}`,
        rows: '3', placeholder: opts.placeholder || '', value: form[key],
        onInput: (e) => { form[key] = e.target.value; },
      })
      : h('input', {
        class: `field-input ${errorMsg ? 'field-input--error' : ''}`,
        type: opts.type || 'text', placeholder: opts.placeholder || '', value: form[key],
        onInput: (e) => { form[key] = e.target.value; },
      });
    return h('div', { class: `field ${opts.half ? 'field--half' : ''}` }, [
      h('label', { class: 'field-label' }, label),
      input,
      errorMsg ? h('span', { class: 'field-error' }, errorMsg) : null,
    ]);
  }

  function renderForm() {
    formSlot.replaceChildren(
      field('destination', 'Destination', { placeholder: 'e.g. Home, City Hospital' }),
      field('reason', 'Reason', { textarea: true, placeholder: 'Briefly explain the purpose of this gate pass (min. 10 characters)' }),
      h('div', { class: 'field-pair' }, [
        field('departureDate', 'Departure date', { type: 'date', half: true }),
        field('departureTime', 'Departure time', { type: 'time', half: true }),
      ]),
      h('div', { class: 'field-pair' }, [
        field('returnDate', 'Expected return date', { type: 'date', half: true }),
        field('returnTime', 'Expected return time', { type: 'time', half: true }),
      ]),
      field('remarks', 'Additional remarks (optional)', { textarea: true, placeholder: 'Anything else the reviewer should know' }),
      h('button', { class: 'btn btn--primary btn--block', type: 'submit', disabled: submitting }, [
        submitting ? h('span', { class: 'spinner spinner--small' }) : icon('plus', { size: 16 }),
        submitting ? 'Submitting…' : 'Submit Gate Pass Request',
      ]),
    );
  }

  function handleSubmit(e) {
    e.preventDefault();
    const result = validateGatePassForm(form);
    errors = result.errors;
    renderForm();
    if (!result.isValid) return;

    openModal({
      title: 'Confirm submission',
      body: h('div', {}, [
        h('p', {}, 'Are you sure you want to submit this gate-pass request?'),
        h('div', { class: 'confirm-summary' }, [
          h('p', {}, [h('strong', {}, 'Destination: '), form.destination]),
          h('p', {}, [h('strong', {}, 'Departure: '), `${formatDate(form.departureDate)} · ${form.departureTime}`]),
          h('p', {}, [h('strong', {}, 'Return: '), `${formatDate(form.returnDate)} · ${form.returnTime}`]),
        ]),
      ]),
      actions: [
        { label: 'Cancel', variant: 'secondary', onClick: (close) => close() },
        { label: 'Confirm Submission', variant: 'primary', onClick: async (close) => { close(); await doSubmit(); } },
      ],
    });
  }

  async function doSubmit() {
    submitting = true;
    renderForm();
    try {
      await submitGatePass(form);
      showToast('Gate-pass request submitted successfully.', 'success');
      Object.keys(form).forEach((k) => { form[k] = ''; });
      errors = {};
      loadHistory();
    } catch {
      showToast('Unable to submit gate pass. Please try again.', 'error');
    } finally {
      submitting = false;
      renderForm();
    }
  }

  function renderHistory() {
    if (historyState.status === 'loading') { historySlot.replaceChildren(LoadingState('Loading gate pass history…')); return; }
    if (historyState.status === 'error') { historySlot.replaceChildren(ErrorState('Unable to load gate pass history. Please try again.', loadHistory)); return; }
    if (!historyState.items.length) { historySlot.replaceChildren(EmptyState('No gate pass requests yet.', 'door')); return; }
    historySlot.replaceChildren(h('div', { class: 'gatepass-list' }, historyState.items.map((gp) => GatePassCard(gp, onOpenDetails))));
  }

  async function loadHistory() {
    historyState.status = 'loading';
    renderHistory();
    try {
      historyState.items = await getMyGatePasses();
      historyState.status = 'success';
    } catch { historyState.status = 'error'; }
    renderHistory();
  }

  renderForm();
  loadHistory();
  return root;
}
