import { api } from '../services/index.js';
import { esc } from '../ui/components.js';

export async function render(main) {
  const s = await api.getProfile();
  const rows = [['Name', s.name], ['Student ID', s.id], ['Department', s.department], ['Year', s.year], ['Division', s.division], ['Roll number', s.rollNo], ['Email', s.email], ['Phone', s.phone], ['Head of department', s.hod]];
  main.innerHTML = `<section class="card"><dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></section>`;
}
