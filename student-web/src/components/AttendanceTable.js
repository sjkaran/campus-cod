import { h } from '../utils/dom.js';
import { formatDate, formatPercentage } from '../utils/formatting.js';
import { StatusBadge } from './StatusBadge.js';

/** @param {import('../models/models.js').SubjectAttendance[]} subjects */
export function SubjectAttendanceTable(subjects, threshold) {
  const wrap = h('div', { class: 'table-scroll' });
  const table = h('table', { class: 'data-table' }, [
    h('thead', {}, h('tr', {}, [
      h('th', {}, 'Subject'),
      h('th', {}, 'Classes'),
      h('th', {}, 'Present'),
      h('th', {}, 'Absent'),
      h('th', {}, 'Attendance'),
    ])),
    h('tbody', {}, subjects.map((s) => h('tr', {}, [
      h('td', { class: 'data-table__primary' }, s.subject),
      h('td', {}, String(s.totalClasses)),
      h('td', {}, String(s.present)),
      h('td', {}, String(s.absent)),
      h('td', {}, [
        h('div', { class: 'inline-meter' }, [
          h('div', { class: 'inline-meter__track' }, h('div', {
            class: `inline-meter__fill ${s.percentage < threshold ? 'inline-meter__fill--warning' : ''}`,
            style: `width:${Math.min(100, s.percentage)}%`,
          })),
          h('span', { class: s.percentage < threshold ? 'text-warning' : '' }, formatPercentage(s.percentage)),
        ]),
      ]),
    ]))),
  ]);
  wrap.appendChild(table);
  return wrap;
}

/** @param {import('../models/models.js').AttendanceRecord[]} records */
export function AttendanceHistoryTable(records) {
  const wrap = h('div', { class: 'table-scroll' });
  const table = h('table', { class: 'data-table' }, [
    h('thead', {}, h('tr', {}, [
      h('th', {}, 'Date'),
      h('th', {}, 'Subject'),
      h('th', {}, 'Session'),
      h('th', {}, 'Status'),
    ])),
    h('tbody', {}, records.map((r) => h('tr', {}, [
      h('td', {}, formatDate(r.date)),
      h('td', { class: 'data-table__primary' }, r.subject),
      h('td', {}, r.session),
      h('td', {}, StatusBadge(r.status, r.status)),
    ]))),
  ]);
  wrap.appendChild(table);
  return wrap;
}
