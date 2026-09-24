import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { getAttendanceSummary, getSubjectAttendance, getAttendanceHistory } from '../services/attendanceService.js';
import { StatCard } from '../components/StatCard.js';
import { SubjectAttendanceTable, AttendanceHistoryTable } from '../components/AttendanceTable.js';
import { LoadingState, ErrorState, EmptyState } from '../components/DataState.js';

export function AttendancePage() {
  const state = {
    summary: null, subjects: [], history: [],
    filters: { subject: 'all', status: 'all', fromDate: '', toDate: '' },
    summaryStatus: 'loading', subjectsStatus: 'loading', historyStatus: 'loading',
  };

  const root = h('div', { class: 'page' });
  const summarySlot = h('div', { class: 'panel' }, LoadingState('Loading attendance…'));
  const warningSlot = h('div', {});
  const subjectsSlot = h('div', { class: 'panel' }, LoadingState('Loading subjects…'));
  const historySlot = h('div', {});

  root.append(
    h('div', { class: 'page__head' }, h('h2', { class: 'page__title' }, 'Attendance')),
    summarySlot,
    warningSlot,
    subjectsSlot,
    h('div', { class: 'panel' }, [
      h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Attendance History')),
      buildFilters(),
      historySlot,
    ]),
  );

  function buildFilters() {
    const subjectSelect = h('select', { class: 'field-input field-input--select', onChange: (e) => { state.filters.subject = e.target.value; loadHistory(); } }, [
      h('option', { value: 'all' }, 'All subjects'),
      ...state.subjects.map((s) => h('option', { value: s.subject }, s.subject)),
    ]);
    const statusSelect = h('select', { class: 'field-input field-input--select', onChange: (e) => { state.filters.status = e.target.value; loadHistory(); } }, [
      h('option', { value: 'all' }, 'All statuses'),
      h('option', { value: 'Present' }, 'Present'),
      h('option', { value: 'Absent' }, 'Absent'),
    ]);
    const fromInput = h('input', { type: 'date', class: 'field-input', 'aria-label': 'From date', onChange: (e) => { state.filters.fromDate = e.target.value; loadHistory(); } });
    const toInput = h('input', { type: 'date', class: 'field-input', 'aria-label': 'To date', onChange: (e) => { state.filters.toDate = e.target.value; loadHistory(); } });

    return h('div', { class: 'filters-row' }, [
      icon('filter', { size: 16, class: 'filters-row__icon' }),
      subjectSelect, statusSelect, fromInput, h('span', { class: 'filters-row__sep' }, '–'), toInput,
    ]);
  }

  async function loadSummary() {
    state.summaryStatus = 'loading';
    renderSummary();
    try {
      state.summary = await getAttendanceSummary();
      state.summaryStatus = 'success';
    } catch { state.summaryStatus = 'error'; }
    renderSummary();
    renderWarning();
  }

  function renderSummary() {
    if (state.summaryStatus === 'loading') { summarySlot.replaceChildren(LoadingState('Loading attendance…')); return; }
    if (state.summaryStatus === 'error') { summarySlot.replaceChildren(ErrorState('Unable to load attendance data. Please try again.', loadSummary)); return; }
    const s = state.summary;
    summarySlot.replaceChildren(h('div', { class: 'stat-row' }, [
      StatCard({ label: 'Overall Attendance', value: `${s.percentage}%`, tone: s.percentage < s.threshold ? 'warning' : 'good', iconName: 'check-circle' }),
      StatCard({ label: 'Total Classes', value: String(s.totalClasses) }),
      StatCard({ label: 'Present', value: String(s.present), tone: 'good' }),
      StatCard({ label: 'Absent', value: String(s.absent), tone: 'bad' }),
    ]));
  }

  function renderWarning() {
    if (!state.summary || state.summaryStatus !== 'success') { warningSlot.replaceChildren(); return; }
    const below = state.subjects.filter((s) => s.percentage < state.summary.threshold);
    if (!below.length) { warningSlot.replaceChildren(); return; }
    warningSlot.replaceChildren(h('div', { class: 'alert alert--warning' }, [
      icon('warning', { size: 18 }),
      h('span', {}, `Your attendance in ${below.map((s) => s.subject).join(', ')} is below the required ${state.summary.threshold}% threshold.`),
    ]));
  }

  async function loadSubjects() {
    state.subjectsStatus = 'loading';
    renderSubjects();
    try {
      state.subjects = await getSubjectAttendance();
      state.subjectsStatus = 'success';
    } catch { state.subjectsStatus = 'error'; }
    renderSubjects();
    renderWarning();
    refreshFilters();
  }

  function renderSubjects() {
    const threshold = state.summary ? state.summary.threshold : 75;
    if (state.subjectsStatus === 'loading') { subjectsSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Subject-wise Attendance')), LoadingState('Loading subjects…')); return; }
    if (state.subjectsStatus === 'error') { subjectsSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Subject-wise Attendance')), ErrorState('Unable to load subject attendance. Please try again.', loadSubjects)); return; }
    subjectsSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Subject-wise Attendance')), SubjectAttendanceTable(state.subjects, threshold));
  }

  function refreshFilters() {
    const filtersRow = root.querySelector('.filters-row');
    if (filtersRow) filtersRow.replaceWith(buildFilters());
  }

  async function loadHistory() {
    state.historyStatus = 'loading';
    renderHistory();
    try {
      state.history = await getAttendanceHistory(state.filters);
      state.historyStatus = 'success';
    } catch { state.historyStatus = 'error'; }
    renderHistory();
  }

  function renderHistory() {
    if (state.historyStatus === 'loading') { historySlot.replaceChildren(LoadingState('Loading history…')); return; }
    if (state.historyStatus === 'error') { historySlot.replaceChildren(ErrorState('Unable to load attendance history. Please try again.', loadHistory)); return; }
    if (!state.history.length) { historySlot.replaceChildren(EmptyState('No attendance records found for the selected filters.', 'inbox')); return; }
    historySlot.replaceChildren(AttendanceHistoryTable(state.history));
  }

  loadSummary();
  loadSubjects();
  loadHistory();

  return root;
}
