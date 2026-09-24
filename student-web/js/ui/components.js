export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ICONS = {
  home: '<path d="M3 11l9-8 9 8v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0"/>',
  check: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M9 16l2 2 4-4"/>',
  pass: '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
};
export const icon = (n) => `<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[n]}</svg>`;
export const badge = (t, tone = '') => `<span class="badge ${tone}">${esc(t)}</span>`;
export const GATE_TONE = { PENDING: 'warn', APPROVED: 'ok', REJECTED: 'bad' };
export const fmtDate = (d) => (d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '–');
export const empty = (t, s = '') => `<div class="state"><strong>${esc(t)}</strong><p>${esc(s)}</p></div>`;
export const loading = () => '<div class="state">Loading…</div>';
export const errorState = (m) => `<div class="state err"><strong>Couldn't load this page</strong><p>${esc(m)}</p></div>`;
export const stat = (label, value, sub = '') => `<div class="card stat"><span>${esc(label)}</span><b>${esc(value)}</b><small>${esc(sub)}</small></div>`;
export const noteItem = (n) => `<article class="item"><header><strong>${esc(n.title)}</strong>${badge(n.category)}<span class="muted">${esc(n.source)}, ${fmtDate(n.date)}</span></header><p>${esc(n.body)}</p></article>`;
