import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { getInitials } from '../utils/formatting.js';

/** @param {import('../models/models.js').Student} student */
export function ProfilePage(student) {
  const row = (label, value, iconName) => h('div', { class: 'profile-row' }, [
    icon(iconName, { size: 18, class: 'profile-row__icon' }),
    h('div', {}, [
      h('span', { class: 'field-label' }, label),
      h('p', { class: 'profile-row__value' }, value || '—'),
    ]),
  ]);

  return h('div', { class: 'page' }, [
    h('div', { class: 'page__head' }, h('h2', { class: 'page__title' }, 'Profile')),
    h('div', { class: 'panel profile-panel' }, [
      h('div', { class: 'profile-header' }, [
        h('div', { class: 'avatar avatar--large' }, getInitials(student.name)),
        h('div', {}, [
          h('h3', { class: 'profile-header__name' }, student.name),
          h('p', { class: 'profile-header__meta' }, `${student.department} · Semester ${student.semester} · Section ${student.section}`),
        ]),
      ]),
      h('div', { class: 'profile-grid' }, [
        row('Student ID', student.id, 'user'),
        row('Roll Number', student.rollNumber, 'user'),
        row('Email', student.email, 'mail'),
        row('Phone', student.phone, 'phone'),
        row('Department', student.department, 'building'),
        row('Admission Year', student.admissionYear, 'building'),
      ]),
      h('p', { class: 'profile-panel__note' }, 'Profile details are read-only in this prototype. Editing will be enabled once the student-records API is connected.'),
    ]),
  ]);
}
