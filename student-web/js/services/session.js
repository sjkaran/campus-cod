const KEY = 'sc.student.session';
export const session = {
  get data() { try { return JSON.parse(sessionStorage.getItem(KEY)); } catch { return null; } },
  get token() { return this.data?.token; },
  set(d) { sessionStorage.setItem(KEY, JSON.stringify(d)); },
  clear() { sessionStorage.removeItem(KEY); },
};
