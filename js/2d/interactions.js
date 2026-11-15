// 2D Canvas Viewport, Pointer Events, Snapping, Measurement & Keyboard Shortcuts
import { $, $$, PX_MM, TAP, norm, narrow, toast, esc, fmt, area } from '../config.js';
import { tr, nm } from '../i18n.js';
import { LIB } from '../data/furniture-lib.js';
import { BOUNDS, WALLS, WINS, ROOMS } from '../data/floorplan.js';
import { state, ui, view, getF, aabb, mutate, snap, commit, undo, redo } from './state.js';
import { renderAll, renderSel, renderMeasure, renderFurn } from './renderer.js';
import { renderPanel, renderFab, drawer, closeDrawers } from '../ui/panels.js';

const svg = $('#plan') || $('#svg');

let uidCounter = 1000;
export const uid = () => 'f_' + (++uidCounter) + '_' + Math.random().toString(36).slice(2, 6);

export const typeColor = t => {
  for (const c of LIB) {
    for (const i of c.items) {
      if (i[0] === t) return i[4];
    }
  }
  return '#eee';
};

export const F = (type, name, cx, cy, w, d, rot = 0, color) => ({
  id: uid(),
  type,
  name,
  cx,
  cy,
  w,
  d,
  rot,
  color: color || typeColor(type)
});

export function snapRects(){
  return WALLS.filter((w, i) => !state.demolished.includes('w' + i)).concat(WINS);
}

/* ======================= 操作 ======================= */
export function select(sel){
  ui.sel = sel;
  renderSel();
  renderPanel();
}
if (typeof window !== 'undefined') window.select = select;

export function rotateSel(d){
  if (ui.sel?.kind === 'furn') {
    mutate(() => {
      const f = getF(ui.sel.id);
      if (f) f.rot = norm(f.rot + d);
    });
  }
}

export function deleteSel(){
  if (ui.sel?.kind === 'furn'){
    const id = ui.sel.id;
    ui.sel = null;
    mutate(() => {
      state.furniture = state.furniture.filter(f => f.id !== id);
    });
  }
}

export function duplicateSel(){
  if (ui.sel?.kind === 'furn'){
    const f = getF(ui.sel.id);
    if (!f) return;
    const n = { ...f, id: uid(), cx: f.cx + 200, cy: f.cy + 200 };
    pushOut(n);
    ui.sel = { kind: 'furn', id: n.id };
    mutate(() => state.furniture.push(n));
  }
}

export function pushOut(f){
  for (let k = 0; k < 6; k++){
    const b = aabb(f);
    let moved = false;
    for (const [x0, y0, x1, y1] of snapRects()){
      if (b[2] > x0 && b[0] < x1 && b[3] > y0 && b[1] < y1){
        const ox1 = x1 - b[0], ox2 = b[2] - x0, oy1 = y1 - b[1], oy2 = b[3] - y0;
        const m = Math.min(ox1, ox2, oy1, oy2);
        if (m === ox1) f.cx += ox1 + 10;
        else if (m === ox2) f.cx -= ox2 + 10;
        else if (m === oy1) f.cy += oy1 + 10;
        else f.cy -= oy2 + 10;
        moved = true;
        break;
      }
    }
    if (!moved) return;
  }
}

export function addItem(it, x, y){
  const [type, name, w, d, color] = it;
  const f = F(type, name, Math.round(x / 10) * 10, Math.round(y / 10) * 10, w, d, 0, color);
  pushOut(f);
  ui.sel = { kind: 'furn', id: f.id };
  mutate(() => (type === 'rug' ? state.furniture.unshift(f) : state.furniture.push(f)));
  toast(tr(`تمت إضافة «${nm(name)}» ${w}×${d}`, `Added "${nm(name)}" ${w}×${d}`));
}

export function toggleWall(id){
  const w = WALLS[+id.slice(1)];
  if (w[4] === 'b') return toast(tr('الجدران الحاملة (السوداء) لا يمكن هدمها', 'Load-bearing walls cannot be removed'));
  if (w[4] === 'e') return toast(tr('الجدران الخارجية جزء من واجهة المبنى ولا يمكن حذفها', 'Exterior envelope walls cannot be removed'));
  const on = state.demolished.includes(id);
  mutate(() => {
    state.demolished = on ? state.demolished.filter(x => x !== id) : [...state.demolished, id];
  });
  toast(on ? tr('تمت استعادة الجدار', 'Wall restored') : tr(`تم تحديد هدم الجدار (${Math.max(w[2]-w[0], w[3]-w[1])} مم)`, `Marked wall for demolition`));
}

export function setTool(t){
  ui.tool = t;
  document.querySelectorAll('#tools .btn').forEach(b => b.classList.toggle('on', b.dataset.tool === t));
  if (svg) svg.setAttribute('class', 'tool-' + t);
  syncModeHint();
  if (t !== 'select') select(null);
  if (t !== 'measure' && ui.mA){
    ui.mA = null;
    renderMeasure();
  }
}

export function syncModeHint(){
  const m = $('#modehint');
  if (!m) return;
  m.textContent = ui.tool === 'demolish'
    ? tr('وضع تعديل وهدم الجدران · انقر على جدار غير حامل لحذفه أو استعادته', 'Wall Edit Mode')
    : (ui.tool === 'measure' ? tr('وضع قياس الأبعاد الهندسية · اسحب خطا للقياس بالمليمتر', 'Measurement Mode') : '');
  m.classList.toggle('show', ui.tool !== 'select');
}

/* ======================= 视图 ======================= */
export function applyView(){
  if (!svg) return;
  const W = svg.clientWidth || window.innerWidth, H = svg.clientHeight || window.innerHeight;
  svg.setAttribute('viewBox', `${view.x0} ${view.y0} ${W / view.s} ${H / view.s}`);
  renderSel();
  if (ui.mA) renderMeasure();
  const sc = $('#scale');
  if (sc) sc.textContent = Math.round(view.s * 100) + '%';
}

export function fitView(){
  if (!svg) return;
  const W = svg.clientWidth || window.innerWidth, H = svg.clientHeight || window.innerHeight;
  const pad = 1200;
  const bw = BOUNDS.w + pad * 2, bh = BOUNDS.h + pad * 2;
  view.s = Math.min((W - 40) / bw, (H - 40) / bh);
  view.x0 = BOUNDS.x - pad + (bw - W / view.s) / 2;
  view.y0 = BOUNDS.y - pad + (bh - H / view.s) / 2;
  applyView();
}

export function zoomAt(ns, sx, sy){
  const os = view.s;
  ns = Math.max(0.012, Math.min(2.0, ns));
  view.x0 += sx / os - sx / ns;
  view.y0 += sy / os - sy / ns;
  view.s = ns;
  applyView();
}

export const zoomCenter = k => {
  if (!svg) return;
  zoomAt(view.s * k, svg.clientWidth / 2, svg.clientHeight / 2);
};

export const setRatio = r => {
  if (!svg) return;
  zoomAt(1 / (r * PX_MM), svg.clientWidth / 2, svg.clientHeight / 2);
};

export function toMM(e){
  if (!svg) return { x: 0, y: 0 };
  const pt = svg.createSVGPoint();
  pt.x = e.clientX;
  pt.y = e.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

export function toScreen(x, y){
  return [(x - view.x0) * view.s, (y - view.y0) * view.s];
}

export function snapMove(f, tx, ty){
  if (!ui.layers?.wallSnap) return [Math.round(tx / 10) * 10, Math.round(ty / 10) * 10];
  const w = f.w, d = f.d, rad = (f.rot * Math.PI) / 180, c = Math.abs(Math.cos(rad)), s = Math.abs(Math.sin(rad));
  const hw = (w * c + d * s) / 2, hd = (w * s + d * c) / 2;
  let nx = tx, ny = ty, dxMin = 80, dyMin = 80;

  for (const [x0, y0, x1, y1] of snapRects()){
    for (const x of [x0 - hw, x1 + hw]){
      if (Math.abs(tx - x) < dxMin && ty + hd > y0 && ty - hd < y1){
        dxMin = Math.abs(tx - x);
        nx = x;
      }
    }
    for (const y of [y0 - hd, y1 + hd]){
      if (Math.abs(ty - y) < dyMin && tx + hw > x0 && tx - hw < x1){
        dyMin = Math.abs(ty - y);
        ny = y;
      }
    }
  }
  return [Math.round(nx / 10) * 10, Math.round(ny / 10) * 10];
}

export function snapPoint(p, orth){
  let x = Math.round(p.x / 10) * 10, y = Math.round(p.y / 10) * 10;
  if (orth && ui.mA){
    const dx = Math.abs(x - ui.mA.x), dy = Math.abs(y - ui.mA.y);
    if (dx > dy) y = ui.mA.y;
    else x = ui.mA.x;
  }
  if (!ui.layers?.wallSnap) return { x, y };

  let dMin = 140, pt = { x, y };
  for (const [x0, y0, x1, y1] of snapRects()){
    for (const cx of [x0, x1]){
      for (const cy of [y0, y1]){
        const d = Math.hypot(p.x - cx, p.y - cy);
        if (d < dMin){
          dMin = d;
          pt = { x: cx, y: cy };
        }
      }
    }
  }
  return pt;
}

/* ======================= 事件交互 (Pointer / Touch) ======================= */
let drag = null, touches = new Map(), pinch = null;
const pinchInfo = () => {
  const [a, b] = Array.from(touches.values());
  return { d: Math.hypot(a.x - b.x, a.y - b.y), c: [(a.x + b.x) / 2, (a.y + b.y) / 2] };
};

const svgXY = (x, y) => {
  if (!svg) return [x, y];
  const r = svg.getBoundingClientRect();
  return [x - r.left, y - r.top];
};

function endDrag(cancel){
  if (!drag) return;
  const d = drag;
  drag = null;
  if (svg) svg.classList.remove('panning');
  if (d.kind === 'measure'){
    if (!cancel && d.moved && ui.mA && ui.mCur){
      if (Math.hypot(ui.mCur.x - ui.mA.x, ui.mCur.y - ui.mA.y) > 20){
        mutate(() => state.measures.push({ a: ui.mA, b: ui.mCur }));
      }
      ui.mA = null;
      ui.mCur = null;
    }
    renderMeasure();
    return;
  }
  if (d.kind === 'pan'){
    if (!cancel && !d.moved && ui.tool === 'select') {
      select(d.room ? { kind: 'room', id: d.room } : null);
    }
    return;
  }
  if (d.moved){
    commit(d.before);
    renderAll();
  }
}

if (svg) {
  svg.addEventListener('pointerdown', e => {
    if (e.button === 1 || e.button === 2) return;
    closeDrawers();
    const menuEl = $('details.menu');
    if (menuEl) menuEl.open = false;

    if (e.pointerType !== 'mouse'){
      touches.set(e.pointerId, { x: e.clientX, y: e.clientY });
      try { svg.setPointerCapture(e.pointerId); } catch(err) {}
      if (touches.size >= 2){
        endDrag(drag?.kind === 'measure' || drag?.kind === 'pan');
        const { d, c } = pinchInfo();
        pinch = { d, c, s: view.s, px: view.x0 + c[0] / view.s, py: view.y0 + c[1] / view.s };
        return;
      }
    }
    if (pinch) return;
    const p = toMM(e), t = e.target;
    if (ui.tool === 'measure'){
      const q = snapPoint(p, e.shiftKey);
      if (!ui.mA){
        ui.mA = q;
        ui.mCur = q;
        drag = { kind: 'measure', sx: e.clientX, sy: e.clientY, moved: false };
        try { svg.setPointerCapture(e.pointerId); } catch(err) {}
      } else {
        const a = ui.mA;
        ui.mA = null;
        ui.mCur = null;
        if (Math.hypot(q.x - a.x, q.y - a.y) > 20) mutate(() => state.measures.push({ a, b: q }));
      }
      renderMeasure();
      return;
    }

    const h = t.closest('[data-handle]');
    if (h && ui.sel?.kind === 'furn'){
      drag = { kind: h.dataset.handle, id: ui.sel.id, sx: e.clientX, sy: e.clientY, before: snap(), moved: false };
    } else if (ui.tool === 'demolish' && t.closest('[data-wall]')){
      toggleWall(t.closest('[data-wall]').dataset.wall);
      return;
    } else if (ui.tool === 'select' && t.closest('[data-fid]')){
      const f = getF(t.closest('[data-fid]').dataset.fid);
      if (f) {
        if (ui.sel?.id !== f.id) select({ kind: 'furn', id: f.id });
        drag = { kind: 'move', id: f.id, sx: e.clientX, sy: e.clientY, ox: p.x - f.cx, oy: p.y - f.cy, before: snap(), moved: false };
      }
    } else {
      const room = t.closest('[data-room]');
      drag = { kind: 'pan', sx: e.clientX, sy: e.clientY, x0: view.x0, y0: view.y0, room: room && room.dataset.room, moved: false };
    }
    try { svg.setPointerCapture(e.pointerId); } catch(err) {}
  });

  svg.addEventListener('pointermove', e => {
    if (touches.has(e.pointerId)) touches.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch){
      if (touches.size < 2) return;
      const { d, c } = pinchInfo();
      const ns = Math.max(0.012, Math.min(2, (pinch.s * d) / pinch.d));
      view.s = ns;
      view.x0 = pinch.px - c[0] / ns;
      view.y0 = pinch.py - c[1] / ns;
      applyView();
      return;
    }
    const p = toMM(e);
    const cxEl = $('#cx'), cyEl = $('#cy');
    if (cxEl) cxEl.textContent = Math.round(p.x) + ' mm';
    if (cyEl) cyEl.textContent = Math.round(p.y) + ' mm';

    if (!drag){
      const room = e.target.closest && e.target.closest('[data-room]');
      const hoverEl = $('#hover');
      if (hoverEl) {
        hoverEl.innerHTML = room ? `<b>${esc(state.rooms[room.dataset.room].name)}</b> ${fmt(area(ROOMS.find(r => r.id === room.dataset.room).poly))} m²` : '';
      }
      if (ui.tool === 'measure' && ui.mA){
        ui.mCur = snapPoint(p, e.shiftKey);
        renderMeasure();
      }
      return;
    }

    const far = Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) >= TAP;
    if (drag.kind === 'measure'){
      if (far) drag.moved = true;
      ui.mCur = snapPoint(p, e.shiftKey);
      renderMeasure();
      return;
    }
    if (drag.kind === 'pan'){
      if (!drag.moved && !far) return;
      drag.moved = true;
      svg.classList.add('panning');
      view.x0 = drag.x0 - (e.clientX - drag.sx) / view.s;
      view.y0 = drag.y0 - (e.clientY - drag.sy) / view.s;
      applyView();
      return;
    }

    const f = getF(drag.id);
    if (!f || (!drag.moved && !far)) return;
    drag.moved = true;

    if (drag.kind === 'move'){
      [f.cx, f.cy] = snapMove(f, p.x - drag.ox, p.y - drag.oy);
    } else if (drag.kind === 'rot'){
      const a = (Math.atan2(p.y - f.cy, p.x - f.cx) * 180) / Math.PI + 90;
      f.rot = norm(e.shiftKey ? a : Math.round(a / 15) * 15);
    } else if (drag.kind === 'size'){
      const a = (f.rot * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
      const dx = p.x - f.cx, dy = p.y - f.cy, lx = dx * c + dy * s, ly = -dx * s + dy * c;
      const ax = -f.w / 2, ay = -f.d / 2;
      const nw = Math.max(100, Math.round((lx - ax) / 10) * 10);
      const nd = Math.max(100, Math.round((ly - ay) / 10) * 10);
      const mx = ax + nw / 2, my = ay + nd / 2;
      f.cx += mx * c - my * s;
      f.cy += mx * s + my * c;
      f.w = nw;
      f.d = nd;
    }
    renderFurn();
    renderSel();
  });

  function onPointerEnd(e){
    touches.delete(e.pointerId);
    if (pinch){
      if (touches.size < 2) pinch = null;
      return;
    }
    endDrag(e.type === 'pointercancel');
  }

  svg.addEventListener('pointerup', onPointerEnd);
  svg.addEventListener('pointercancel', onPointerEnd);

  ['gesturestart', 'gesturechange', 'gestureend'].forEach(t =>
    document.addEventListener(t, e => e.preventDefault())
  );

  svg.addEventListener('wheel', e => {
    e.preventDefault();
    const r = svg.getBoundingClientRect();
    zoomAt(view.s * Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)), e.clientX - r.left, e.clientY - r.top);
  }, { passive: false });

  svg.addEventListener('dblclick', e => {
    if (ui.tool === 'select' && e.target.closest('[data-fid]')) rotateSel(90);
  });

  svg.addEventListener('contextmenu', e => {
    if (ui.tool === 'measure'){
      e.preventDefault();
      ui.mA = null;
      renderMeasure();
    }
  });
}

/* ======================= 键盘快捷键 ======================= */
document.addEventListener('keydown', e => {
  if (e.target.matches('input,select,textarea')) return;
  if (window.View3D?.walking && window.View3D.walking()) return;
  const mod = e.metaKey || e.ctrlKey, k = e.key.toLowerCase();

  if (mod && k === 'z'){
    e.preventDefault();
    e.shiftKey ? redo() : undo();
  } else if (mod && (k === 'y' || (e.shiftKey && k === 'z'))){
    e.preventDefault();
    redo();
  } else if (k === 'delete' || k === 'backspace'){
    deleteSel();
  } else if (k === 'r'){
    rotateSel(e.shiftKey ? -90 : 90);
  } else if (k === 'd' && mod){
    e.preventDefault();
    duplicateSel();
  } else if (k === 'f' && e.shiftKey){
    e.preventDefault();
    const fsBtn = $('#fullscreen');
    if (fsBtn) fsBtn.click();
  } else if (k === ' '){
    e.preventDefault();
    fitView();
  } else if (k === 'v'){
    setTool('select');
  } else if (k === 'm'){
    setTool('measure');
  } else if (k === 'x'){
    setTool('demolish');
  } else if (k === 'escape'){
    if (ui.mA){
      ui.mA = null;
      renderMeasure();
    } else {
      if (ui.tool !== 'select') setTool('select');
      select(null);
    }
  } else if (k === '+' || k === '='){
    zoomCenter(1.25);
  } else if (k === '-'){
    zoomCenter(0.8);
  }
});
