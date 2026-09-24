import { api } from '../services/index.js';
import { esc, badge, fmtDate, empty, GATE_TONE } from '../ui/components.js';

const today = () => new Date().toISOString().slice(0, 10);

// UI-level checks only. The backend must enforce the real rules.
function validate(v) {
  if (Object.values(v).some((x) => !x.trim())) return 'Fill in every field.';
  if (v.outDate < today()) return 'Exit date cannot be in the past.';
  if (v.returnTime <= v.outTime) return 'Return time must be after exit time.';
  if (v.reason.trim().length < 10) return 'Give a fuller reason (at least 10 characters).';
  return '';
}
const table = (list) => list.length
  ? `<div class="scroll"><table><thead><tr><th>Request</th><th>Exit</th><th>Destination</th><th>Status</th><th>HOD remarks</th></tr></thead><tbody>${list.map((p) =>
      `<tr><td>${esc(p.id)}<br><span class="muted">${fmtDate(p.appliedOn)}</span></td><td>${fmtDate(p.outDate)}<br><span class="muted">${esc(p.outTime)} to ${esc(p.returnTime)}</span></td><td>${esc(p.destination)}</td><td>${badge(p.status, GATE_TONE[p.status])}</td><td style="white-space:normal">${esc(p.remarks) || '–'}</td></tr>`).join('')}</tbody></table></div>`
  : empty('No gate pass requests yet', 'Requests you send appear here with the HOD decision.');

export async function render(main) {
  main.innerHTML = `<section class="card"><h2>Apply for a gate pass</h2><form novalidate><div class="fields">
    <label>Exit date<input type="date" name="outDate" min="${today()}"></label>
    <label>Exit time<input type="time" name="outTime"></label>
    <label>Return time<input type="time" name="returnTime"></label>
    <label class="full">Destination<input name="destination"></label>
    <label class="full">Reason<textarea name="reason" rows="3"></textarea></label></div>
    <p class="form-err" role="alert"></p><button class="btn">Send request</button></form></section>
    <section class="card"><h2>My requests</h2><div id="list"></div></section>`;
  const form = main.querySelector('form'), msg = form.querySelector('p'), btn = form.querySelector('button'), list = main.querySelector('#list');
  const say = (t, ok) => { msg.textContent = t; msg.className = ok ? 'form-ok' : 'form-err'; };
  list.innerHTML = table(await api.getGatePasses());
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const v = Object.fromEntries(new FormData(form)), problem = validate(v);
    if (problem) return say(problem);
    btn.disabled = true; say('');
    try { await api.submitGatePass(v); form.reset(); say('Request sent. Your HOD will review it.', true); list.innerHTML = table(await api.getGatePasses()); }
    catch (ex) { say(ex.message); }
    btn.disabled = false;
  });
}
