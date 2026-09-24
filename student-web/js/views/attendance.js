import { api } from '../services/index.js';
import { stat, badge, esc, empty } from '../ui/components.js';

export async function render(main) {
  const { minRequired, overall, subjects } = await api.getAttendance();
  if (!subjects.length) { main.innerHTML = `<div class="card">${empty('No attendance recorded', 'Attendance appears once your faculty submits it.')}</div>`; return; }
  main.innerHTML = `<div class="grid4">${stat('Overall attendance', `${overall}%`, `Minimum required: ${minRequired}%`)}</div>
    <section class="card scroll"><table><thead><tr><th>Subject</th><th>Faculty</th><th>Attended</th><th>Percentage</th><th>Status</th></tr></thead><tbody>
    ${subjects.map((s) => { const ok = s.percentage >= minRequired; return `<tr><td><strong>${esc(s.subject)}</strong><br><span class="muted">${esc(s.code)}</span></td><td>${esc(s.faculty)}</td><td>${s.attended} / ${s.total}</td>
      <td><div class="bar ${ok ? '' : 'low'}"><i style="width:${Math.min(s.percentage, 100)}%"></i></div>${s.percentage}%</td><td>${ok ? badge('On track', 'ok') : badge('Below minimum', 'bad')}</td></tr>`; }).join('')}
    </tbody></table></section>`;
}
