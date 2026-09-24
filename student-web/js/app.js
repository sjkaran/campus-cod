import { session } from './services/session.js';
import { icon, esc, loading, errorState } from './ui/components.js';
import * as login from './views/login.js';
import * as dashboard from './views/dashboard.js';
import * as notifications from './views/notifications.js';
import * as attendance from './views/attendance.js';
import * as gatepass from './views/gatepass.js';
import * as profile from './views/profile.js';

const ROUTES = {
  dashboard: { title: 'Dashboard', icon: 'home', view: dashboard },
  notifications: { title: 'Notifications', icon: 'bell', view: notifications },
  attendance: { title: 'Attendance', icon: 'check', view: attendance },
  'gate-pass': { title: 'Gate pass', icon: 'pass', view: gatepass },
  profile: { title: 'My profile', icon: 'user', view: profile },
};
const app = document.getElementById('app');

async function route() {
  const name = location.hash.replace('#/', '') || 'dashboard';
  // Client-side guard for UX only. The backend enforces real authorization.
  if (!session.data) { if (name !== 'login') { location.hash = '#/login'; return; } return login.render(app); }
  if (name === 'login') { location.hash = '#/dashboard'; return; }
  const key = ROUTES[name] ? name : 'dashboard', r = ROUTES[key], s = session.data.student;
  app.innerHTML = `<div class="shell"><aside class="nav"><div class="brand">Smart Campus</div>
    <nav>${Object.entries(ROUTES).map(([k, x]) => `<a href="#/${k}" class="${k === key ? 'on' : ''}">${icon(x.icon)}${x.title}</a>`).join('')}</nav>
    <button class="link" id="out">Sign out</button></aside>
    <div><header class="top"><h1>${r.title}</h1><span class="muted">${esc(s.name)}, ${esc(s.id)}</span></header><main id="view">${loading()}</main></div></div>`;
  app.querySelector('#out').addEventListener('click', () => { if (confirm('Sign out of Smart Campus?')) { session.clear(); location.hash = '#/login'; } });
  const main = app.querySelector('#view');
  try { await r.view.render(main); } catch (e) { main.innerHTML = errorState(e.message); }
}
addEventListener('hashchange', route);
route();
