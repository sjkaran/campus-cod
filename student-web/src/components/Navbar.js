import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { getInitials } from '../utils/formatting.js';

/**
 * @param {Object} opts
 * @param {string} opts.pageTitle
 * @param {import('../models/models.js').Student} opts.student
 * @param {()=>void} opts.onMenuToggle
 */
export function Navbar({ pageTitle, student, onMenuToggle }) {
  return h('header', { class: 'topbar' }, [
    h('button', { class: 'icon-button topbar__menu', onClick: onMenuToggle, 'aria-label': 'Toggle navigation' }, icon('menu', { size: 20 })),
    h('h1', { class: 'topbar__title' }, pageTitle),
    h('div', { class: 'topbar__spacer' }),
    h('div', { class: 'topbar__identity' }, [
      h('div', { class: 'avatar' }, student ? getInitials(student.name) : '…'),
      h('div', { class: 'topbar__identity-text' }, [
        h('span', { class: 'topbar__name' }, student ? student.name : 'Loading…'),
        h('span', { class: 'topbar__role' }, student ? `${student.department} · Sem ${student.semester}` : ''),
      ]),
    ]),
  ]);
}
