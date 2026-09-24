import { api } from '../services/index.js';
import { noteItem, esc, empty } from '../ui/components.js';

export async function render(main) {
  const notes = await api.getNotifications();
  if (!notes.length) { main.innerHTML = `<div class="card">${empty('No notifications yet', 'Announcements from the admin office and your HOD appear here.')}</div>`; return; }
  const cats = ['All', ...new Set(notes.map((n) => n.category))];
  let active = 'All';
  const draw = () => {
    main.innerHTML = `<div class="chips">${cats.map((c) => `<button class="chip ${c === active ? 'on' : ''}" data-c="${esc(c)}">${esc(c)}</button>`).join('')}</div>
      <section class="card">${notes.filter((n) => active === 'All' || n.category === active).map(noteItem).join('')}</section>`;
    main.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => { active = b.dataset.c; draw(); }));
  };
  draw();
}
