// UI Header, Furniture Library Drag & Drop, File Operations & View Mode Switcher
import { $, $$, COARSE, TAP, esc, bbox, narrow } from '../config.js';
import { tr, nm, LANG, setLang, TIPS } from '../i18n.js';
import { LIB } from '../data/furniture-lib.js';
import { BOUNDS, WALLS, WINS, ROOMS } from '../data/floorplan.js';
import { state, ui, view, defaultState, fixState, mutate, snap, commit, undo, redo } from '../2d/state.js';
import { renderAll, renderOpenings, renderDims, buildDefs, furnSVG } from '../2d/renderer.js';
import { select, pushOut, toMM, applyView, fitView, uid, addItem, setTool, zoomCenter, setRatio } from '../2d/interactions.js';
import { drawer, syncPaneBtns, closeDrawers, clearLayout } from './panels.js';

export let viewMode = '2d';
let switching = false;
export const is3D = () => viewMode === '3d';
window.is3D = is3D;

let toastT;
export function toast(msg){
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove('show'), 2200);
}
window.toast = toast;

export function updateHeader(){
  const u = $('#undo'), re = $('#redo');
  if (u) { u.disabled = !window.undoStack?.length; u.style.opacity = window.undoStack?.length ? 1 : 0.4; }
  if (re) { re.disabled = !window.redoStack?.length; re.style.opacity = window.redoStack?.length ? 1 : 0.4; }
  if (is3D() && window.View3D?.sync) window.View3D.sync();
}
window.updateHeader = updateHeader;

const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement;
export function toggleFullscreen(){
  const de = document.documentElement;
  if (fsEl()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
  else {
    const req = de.requestFullscreen || de.webkitRequestFullscreen;
    if (!req) return toast(tr('الوضع ملء الشاشة غير مدعوم في هذا المتصفح', 'Fullscreen is not supported in this browser'));
    Promise.resolve(req.call(de)).catch(() => toast(tr('تعذر الدخول إلى وضع ملء الشاشة', 'Could not enter fullscreen')));
  }
}
export function syncFullscreen(){
  const on = !!fsEl(), b = $('#fullscreen');
  if (b) {
    b.textContent = '⛶ ' + (on ? tr('إنهاء ملء الشاشة', 'Exit fullscreen') : tr('ملء الشاشة', 'Fullscreen'));
    b.title = (on ? tr('إنهاء ملء الشاشة', 'Exit fullscreen') : tr('ملء الشاشة', 'Fullscreen')) + ' (Shift+F)';
    b.classList.toggle('on', on);
  }
}

export function syncModeHint(){
  const m = $('#modehint');
  if (!m) return;
  m.textContent = ui.tool === 'demolish'
    ? tr('وضع تعديل الجدران (انقر على جدار لحذفه/استعادته)', 'Wall Demolition Mode')
    : (ui.tool === 'measure' ? tr('وضع قياس الأبعاد (اسحب خطا للقياس)', 'Measurement Mode') : '');
  m.classList.toggle('show', ui.tool !== 'select');
}

/* ======================= Furniture Library ======================= */
const itemOf = el => {
  const [ci, ii] = el.dataset.key.split(':').map(Number);
  return LIB[ci].items[ii];
};

export function buildLib(){
  const libEl = $('#lib');
  if (!libEl) return;
  libEl.innerHTML = LIB.map((c, ci) => `<h4>${nm(c.cat)}</h4><div class="lib-grid">${c.items.map((it, ii) => {
    const [t, n, w, d, col] = it, pad = Math.max(w, d) * 0.08;
    return `<div class="item" data-key="${ci}:${ii}" title="${tr('انقر للإضافة أو اسحب إلى المخطط', 'Click to add or drag onto the plan')}">
      <svg viewBox="${-w/2-pad} ${-d/2-pad} ${w+2*pad} ${d+2*pad}">${furnSVG(t, w, d, col)}</svg><b>${esc(nm(n))}</b><small>${w}×${d}</small></div>`;
  }).join('')}</div>`).join('') + `<div class="hint">${tr(
    `جميع قطع الأثاث مرسومة بأبعاد هندسية حقيقية بالمليمتر (mm). ${COARSE ? 'انقر لوضعها في المنتصف، أو اسحبها إلى المخطط أو المشهد ثلاثي الأبعاد.' : 'انقر للإضافة أو اسحب مباشرة إلى المخطط أو المشهد ثلاثي الأبعاد.'} يمكنك تعديل الأبعاد والألوان في اللوحة الجانبية.`,
    `Furniture is rendered at 1:1 real-world millimeters (mm). ${COARSE ? 'Tap to place at center or drag to plan/3D floor.' : 'Click to add or drag directly onto the floorplan or 3D scene.'} Edit sizes and materials in the sidebar.`
  )}</div>`;

  libEl.querySelectorAll('.item').forEach(el => el.addEventListener('pointerdown', e => {
    if (e.button) return;
    libDrag = { el, id: e.pointerId, sx: e.clientX, sy: e.clientY, it: itemOf(el), ghost: null };
  }));
}

let libDrag = null;
function dropPoint(x, y){
  const stage = $('#stage');
  if (!stage) return null;
  const r = stage.getBoundingClientRect();
  if (x < r.left || x > r.right || y < r.top || y > r.bottom) return null;
  if (document.elementFromPoint(x, y)?.closest('aside.open,#fab,#walkOverlay,#joy,#walkExit')) return null;
  if (is3D()) return window.View3D?.groundAt(x, y) || null;
  const p = toMM({ clientX: x, clientY: y });
  return { x: p.x, y: p.y, s: view.s };
}

addEventListener('pointermove', e => {
  if (!libDrag || e.pointerId !== libDrag.id) return;
  const { it } = libDrag;
  if (!libDrag.ghost){
    if (Math.hypot(e.clientX - libDrag.sx, e.clientY - libDrag.sy) < TAP) return;
    const g = libDrag.ghost = document.createElement('div');
    g.id = 'ghost';
    g.innerHTML = `<svg viewBox="${-it[2]/2} ${-it[3]/2} ${it[2]} ${it[3]}">${furnSVG(it[0], it[2], it[3], it[4])}</svg>`;
    document.body.appendChild(g);
    libDrag.el.classList.add('dragging');
  }
  const g = libDrag.ghost;
  const s = Math.max(dropPoint(e.clientX, e.clientY)?.s || (is3D() ? 0.05 : view.s), 0.02);
  Object.assign(g.style, {
    width: Math.max(28, it[2] * s) + 'px',
    height: Math.max(20, it[3] * s) + 'px',
    left: e.clientX + 'px',
    top: e.clientY + 'px'
  });
  const lib = $('aside.lib');
  if (narrow() && lib?.classList.contains('open') && e.clientX > lib.getBoundingClientRect().right) drawer(null);
});

function endLibDrag(e, ok){
  if (!libDrag || e.pointerId !== libDrag.id) return;
  const d = libDrag;
  libDrag = null;
  d.el.classList.remove('dragging');
  if (d.ghost){
    d.ghost.remove();
    if (!ok) return;
    const p = dropPoint(e.clientX, e.clientY);
    if (p) addItem(d.it, p.x, p.y);
    else if (is3D() && e.clientX > $('#stage').getBoundingClientRect().left) toast(tr('يرجى الإفلات على أرضية الغرفة', 'Please drop onto the floor'));
    return;
  }
  if (!ok) return;
  let p = null;
  let roomId = null;
  if (ui.sel?.kind === 'room'){
    roomId = ui.sel.id;
  } else if (is3D() && window.View3D?.groundAt){
    const r = $('#stage').getBoundingClientRect();
    p = window.View3D.groundAt(r.left + r.width / 2, r.top + r.height / 2);
  }
  const svgEl = $('#svg');
  if (!p && !roomId && svgEl) p = { x: view.x0 + svgEl.clientWidth / 2 / view.s, y: view.y0 + svgEl.clientHeight / 2 / view.s };
  addItem(d.it, p?.x, p?.y, roomId);
  closeDrawers();
}
addEventListener('pointerup', e => endLibDrag(e, true));
addEventListener('pointercancel', e => endLibDrag(e, false));

/* ======================= Import & Export ======================= */
function download(name, blob){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function exportPNG(){
  if (is3D()) return window.View3D?.shot();
  const svgEl = $('#svg');
  if (!svgEl) return;
  const clone = svgEl.cloneNode(true), W = 3200, H = Math.round(W * BOUNDS.h / BOUNDS.w);
  clone.setAttribute('viewBox', `${BOUNDS.x} ${BOUNDS.y} ${BOUNDS.w} ${BOUNDS.h}`);
  clone.setAttribute('width', W);
  clone.setAttribute('height', H);
  const selG = clone.querySelector('#gSel');
  if (selG) selG.innerHTML = '';
  const gridG = clone.querySelector('#gGrid');
  if (gridG) gridG.innerHTML = `<rect x="-20000" y="-20000" width="55000" height="55000" fill="${ui.layers.grid ? 'url(#grid)' : '#f7f4ee'}"/>`;
  const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  Object.entries({ x: -20000, y: -20000, width: 55000, height: 55000, fill: '#f7f4ee' }).forEach(([k, v]) => bg.setAttribute(k, v));
  if (gridG) clone.insertBefore(bg, gridG);
  const img = new Image();
  img.onload = () => {
    const cv = document.createElement('canvas');
    cv.width = W;
    cv.height = H;
    cv.getContext('2d').drawImage(img, 0, 0, W, H);
    cv.toBlob(b => download(tr('مخطط_الشقة_المزدوجة', 'twin-apartment-floorplan') + '.png', b));
  };
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(clone));
}

/* ======================= 2D / 3D View Switching ======================= */
export async function setView(m){
  if (m === viewMode || switching) return;
  if (!window.View3D) return toast(tr('محرك 3D قيد التحميل...', '3D engine is loading...'));
  switching = true;
  document.body.classList.add('busy');
  viewMode = m;
  document.body.classList.toggle('m3d', m === '3d');
  $('main')?.classList.toggle('is3d', m === '3d');
  if (m === '3d'){
    if (ui.tool !== 'select') setTool('select');
    ui.mA = null;
    await window.View3D.enter();
  } else {
    await window.View3D.exit();
    applyView();
  }
  const tipEl = $('#tip');
  if (tipEl && typeof TIPS === 'function') tipEl.textContent = TIPS()[m] || '';
  switching = false;
  document.body.classList.remove('busy');
}

/* ======================= Toolbar Event Binding ======================= */
export function initToolbar(){
  document.querySelectorAll('.menu-pop .btn').forEach(b => b.addEventListener('click', () => b.closest('details').open = false));
  document.querySelectorAll('#viewSeg .btn').forEach(b => b.onclick = () => setView(b.dataset.view));
  document.querySelectorAll('#tools .btn').forEach(b => b.onclick = () => setTool(b.dataset.tool));
  document.querySelectorAll('#layers .btn').forEach(b => b.onclick = () => {
    const k = b.dataset.layer;
    ui.layers[k] = !ui.layers[k];
    b.classList.toggle('on', ui.layers[k]);
    if (k === 'dims') $('#gDims').setAttribute('display', ui.layers.dims ? 'inline' : 'none');
    else if (k !== 'wallSnap') renderAll();
  });

  const zoomIn = $('#zoomIn'), zoomOut = $('#zoomOut'), fitBtn = $('#fit');
  if (zoomIn) zoomIn.onclick = () => zoomCenter(1.25);
  if (zoomOut) zoomOut.onclick = () => zoomCenter(0.8);
  if (fitBtn) fitBtn.onclick = fitView;

  const s60 = $('#s60'), s100 = $('#s100');
  if (s60) s60.onclick = () => { setRatio(60); toast(tr('تم العرض بمقياس 1:60 الأصلي', 'Showing at scale 1:60')); };
  if (s100) s100.onclick = () => setRatio(100);

  const uBtn = $('#undo'), rBtn = $('#redo'), clearBtn = $('#clearAll');
  if (uBtn) uBtn.onclick = undo;
  if (rBtn) rBtn.onclick = redo;
  if (clearBtn) clearBtn.onclick = clearLayout;

  const fsBtn = $('#fullscreen');
  if (fsBtn) fsBtn.onclick = toggleFullscreen;
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(t => document.addEventListener(t, syncFullscreen));
  if (navigator.standalone || matchMedia('(display-mode: standalone)').matches) {
    if (fsBtn) fsBtn.hidden = true;
  }

  const tgLib = $('#tgLib'), tgPanel = $('#tgPanel');
  if (tgLib) tgLib.onclick = () => drawer('lib');
  if (tgPanel) tgPanel.onclick = () => drawer('panel');

  document.addEventListener('pointerdown', e => {
    const m = $('details.menu');
    if (m?.open && !m.contains(e.target)) m.open = false;
  });
  matchMedia('(max-width:1100px)').addEventListener('change', () => drawer(null));
  drawer(null);

  const expPng = $('#exportPng'), expJson = $('#exportJson'), impJson = $('#importJson'), fileIn = $('#fileIn');
  if (expPng) expPng.onclick = exportPNG;
  if (expJson) expJson.onclick = () => download(tr('مخطط_الشقة_المزدوجة', 'twin-apartment-floorplan') + '.json', new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' }));
  if (impJson && fileIn) {
    impJson.onclick = () => fileIn.click();
    fileIn.onchange = e => {
      const file = e.target.files[0];
      if (!file) return;
      file.text().then(txt => {
        try {
          const s = JSON.parse(txt);
          if (!Array.isArray(s.furniture)) throw new Error('Invalid format');
          const b = snap();
          Object.assign(state, fixState(s));
          ui.sel = null;
          commit(b);
          renderAll();
          toast(tr('تم استيراد المخطط بنجاح', 'Plan imported successfully'));
        } catch (err) {
          toast(tr('صيغة الملف غير صحيحة', 'Invalid file format'));
        }
      });
      e.target.value = '';
    };
  }

  const resetBtn = $('#reset');
  if (resetBtn) {
    resetBtn.onclick = () => {
      if (confirm(tr('هل تريد استعادة التصميم الافتراضي؟ (يمكن التراجع)', 'Reset to default design? (undoable)'))){
        const b = snap();
        Object.assign(state, defaultState());
        ui.sel = null;
        commit(b);
        renderAll();
      }
    };
  }

  const svgEl = $('#svg');
  if (svgEl) {
    let lastW = 0, lastH = 0;
    new ResizeObserver(() => {
      const w = svgEl.clientWidth, h = svgEl.clientHeight;
      if (!w) return;
      if (!lastW) fitView();
      else {
        view.x0 -= (w - lastW) / 2 / view.s;
        view.y0 -= (h - lastH) / 2 / view.s;
        applyView();
      }
      lastW = w;
      lastH = h;
    }).observe(svgEl);
  }

  const langSel = $('#langSel');
  if (langSel) {
    langSel.onclick = e => {
      const l = e.target.closest('[data-lang]')?.dataset.lang;
      if (l && l !== LANG) setLang(l);
    };
  }
}
