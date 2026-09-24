import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { NAV_ITEMS, ROUTES } from '../utils/constants.js';

/**
 * @param {string} activeRoute
 * @param {(route:string)=>void} onNavigate
 * @param {()=>void} onLogout
 */
export function Sidebar(activeRoute, onNavigate, onLogout) {
  const isActive = (route) => activeRoute === route || (route === ROUTES.GATEPASS && activeRoute === ROUTES.GATEPASS_DETAILS);

  const nav = h('nav', { class: 'sidebar__nav' }, NAV_ITEMS.map((item) => h('button', {
    class: `sidebar__link ${isActive(item.route) ? 'sidebar__link--active' : ''}`,
    onClick: () => onNavigate(item.route),
  }, [icon(item.icon, { size: 19 }), h('span', {}, item.label)])));

  const brand = h('div', { class: 'sidebar__brand' }, [
    h('span', { class: 'sidebar__brand-mark' }, 'SC'),
    h('span', { class: 'sidebar__brand-name' }, 'Smart Campus'),
  ]);

  const logout = h('button', { class: 'sidebar__link sidebar__logout', onClick: onLogout }, [
    icon('logout', { size: 19 }),
    h('span', {}, 'Logout'),
  ]);

  return h('aside', { class: 'sidebar', id: 'sidebar' }, [brand, nav, logout]);
}
