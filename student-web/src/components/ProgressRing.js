import { h } from '../utils/dom.js';

/**
 * Renders a circular progress indicator for the overall attendance %.
 * @param {number} percentage
 * @param {number} threshold below which the ring turns to a warning tone
 */
export function ProgressRing(percentage, threshold = 75) {
  const size = 148;
  const stroke = 12;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, percentage));
  const offset = circumference - (clamped / 100) * circumference;
  const tone = percentage < threshold ? 'ring--warning' : 'ring--good';

  const wrapper = h('div', { class: 'progress-ring' });
  wrapper.innerHTML = `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle class="progress-ring__track" cx="${size / 2}" cy="${size / 2}" r="${radius}" stroke-width="${stroke}" fill="none" />
      <circle class="progress-ring__value ${tone}" cx="${size / 2}" cy="${size / 2}" r="${radius}" stroke-width="${stroke}" fill="none"
        stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
        transform="rotate(-90 ${size / 2} ${size / 2})" stroke-linecap="round" />
    </svg>
    <div class="progress-ring__label">
      <span class="progress-ring__pct">${clamped.toFixed(1)}%</span>
      <span class="progress-ring__caption">Attendance</span>
    </div>
  `;
  return wrapper;
}
