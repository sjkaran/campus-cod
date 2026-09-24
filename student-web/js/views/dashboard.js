import { api } from '../services/index.js';
import { stat, noteItem, badge, esc, fmtDate, GATE_TONE, empty } from '../ui/components.js';

export async function render(main) {
  const [att, notes, passes] = await Promise.all([api.getAttendance(), api.getNotifications(), api.getGatePasses()]);
  const low = att.subjects.filter((s) => s.percentage < att.minRequired).length;
  const pending = passes.filter((p) => p.status === 'PENDING').length;
  const last = passes[0];
  main.innerHTML = `<div class="grid4">
    ${stat('Overall attendance', `${att.overall}%`, low ? `${low} subject${low > 1 ? 's' : ''} below ${att.minRequired}%` : 'All subjects on track')}
    ${stat('Notifications', notes.length, notes[0] ? `Latest on ${fmtDate(notes[0].date)}` : 'Nothing new')}
    ${stat('Gate passes pending', pending, last ? `Last: ${last.destination}` : 'No requests yet')}</div>
    <section class="card"><h2>Latest notifications</h2>${notes.slice(0, 3).map(noteItem).join('') || empty('No notifications')}</section>
    <section class="card"><h2>Most recent gate pass</h2>${last ? `<p style="margin:0">${esc(last.destination)} on ${fmtDate(last.outDate)} ${badge(last.status, GATE_TONE[last.status])}</p>` : empty('No gate passes yet', 'Apply from the Gate pass page.')}</section>`;
}
