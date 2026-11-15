// Global Configuration, Utilities and Constants
export const PX_MM = 25.4 / 96;                           // 1 CSS px = 0.2646 mm
export const COARSE = typeof matchMedia !== 'undefined' ? matchMedia('(pointer:coarse)').matches : false; // Touch devices
export const TAP = COARSE ? 9 : 4;                        // Tap threshold in px
export const STORE = 'twin-apartment-luxury-cad-v4';          // LocalStorage state key
export const LANG_KEY = 'twin-apartment-lang';
export const PANES_KEY = 'twin-apartment-panes';

export const narrow = () => matchMedia('(max-width:1100px)').matches;
export const $ = s => document.querySelector(s);
export const $$ = s => Array.from(document.querySelectorAll(s));

export const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
export const fmt = (n, d = 2) => Number(n).toFixed(d);
export const norm = a => ((Math.round(a) % 360) + 360) % 360;

export const area = poly => Math.abs(poly.reduce((a, p, i) => {
  const q = poly[(i + 1) % poly.length];
  return a + p[0] * q[1] - q[0] * p[1];
}, 0)) / 2 / 1e6;

let toastT;
export function toast(msg){
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove('show'), 2200);
}
if (typeof window !== 'undefined') window.toast = toast;

export { aabb } from './2d/state.js';

export const perim = poly => poly.reduce((a, p, i) => {
  const q = poly[(i + 1) % poly.length];
  return a + Math.hypot(q[0] - p[0], q[1] - p[1]);
}, 0) / 1000;

export const bbox = poly => {
  const xs = poly.map(p => p[0]), ys = poly.map(p => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
};

export function hex2rgb(h) {
  h = h.replace('#', '');
  if (h.length === 3) h = h.split('').map(c => c + c).join('');
  const n = parseInt(h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function shade(h, k) {
  const f = v => Math.max(0, Math.min(255, Math.round(v * k)));
  const [r, g, b] = hex2rgb(h);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}

export function rng(seed) {
  return () => {
    seed |= 0;
    seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

export const rgbK = (hex, k) => {
  const n = parseInt(hex.slice(1), 16);
  const f = v => Math.max(0, Math.min(255, Math.round(v * k)));
  return `rgb(${f(n >> 16 & 255)},${f(n >> 8 & 255)},${f(n & 255)})`;
};
