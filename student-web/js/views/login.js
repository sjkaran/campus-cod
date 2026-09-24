import { api } from '../services/index.js';
import { session } from '../services/session.js';

export function render(app) {
  app.innerHTML = `<div class="login"><form class="card" novalidate>
    <h1>Smart Campus</h1><p class="muted" style="margin:0">Sign in with your student ID</p>
    <label>Student ID<input name="id" autocomplete="username"></label>
    <label>Password<input name="pw" type="password" autocomplete="current-password"></label>
    <p class="form-err" role="alert" style="margin:0"></p>
    <button class="btn">Sign in</button>
    <p class="muted" style="margin:0">Demo login: S2021045 / student123</p></form></div>`;
  const form = app.querySelector('form'), err = form.querySelector('.form-err'), btn = form.querySelector('button');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const { id, pw } = Object.fromEntries(new FormData(form));
    if (!id.trim() || !pw) { err.textContent = 'Enter your student ID and password.'; return; }
    btn.disabled = true; err.textContent = '';
    try { session.set(await api.login(id, pw)); location.hash = '#/dashboard'; }
    catch (ex) { err.textContent = ex.message; btn.disabled = false; }
  });
}
