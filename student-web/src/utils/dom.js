// ===== Minimal DOM helper =====
// A small `h()` helper keeps component code declarative without pulling in
// a framework, matching the "no unnecessary dependencies" guidance.

export function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);

  Object.entries(attrs || {}).forEach(([key, value]) => {
    if (value === null || value === undefined || value === false) return;
    if (key === 'class') {
      el.className = value;
    } else if (key === 'html') {
      el.innerHTML = value;
    } else if (key.startsWith('on') && typeof value === 'function') {
      el.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key === 'dataset') {
      Object.entries(value).forEach(([dk, dv]) => { el.dataset[dk] = dv; });
    } else {
      el.setAttribute(key, value);
    }
  });

  const kids = Array.isArray(children) ? children : [children];
  kids.forEach((child) => {
    if (child === null || child === undefined || child === false) return;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  });

  return el;
}

export function clear(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

export function mount(container, el) {
  clear(container);
  container.appendChild(el);
}
