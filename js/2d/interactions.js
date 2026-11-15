// 2D Canvas Viewport, Pointer Events, Snapping, Measurement & Keyboard Shortcuts
import { $, $$, PX_MM, TAP, norm, narrow } from '../config.js';
import { tr } from '../i18n.js';
import { BOUNDS, WALLS, WINS } from '../data/floorplan.js';
import { state, ui, view, getF, aabb, mutate, snap, commit, undo, redo } from './state.js';
import { renderAll, renderSel } from './renderer.js';
import { renderPanel, renderFab, drawer, closeDrawers } from '../ui/panels.js';

let uidCounter = 1000;
export const uid = () => 'f_' + (++uidCounter) + '_' + Math.random().toString(36).slice(2, 6);

export function snapRects(){
  return WALLS.filter((w, i) => !state.demolished.includes('w' + i)).concat(WINS);
}

/* ======================= 操作 ======================= */
export function select(sel){ ui.sel = sel; renderSel(); renderPanel(); }
export function rotateSel(d){ if (ui.sel?.kind==='furn') mutate(() => { const f = getF(ui.sel.id); f.rot = norm(f.rot + d); }); }
export function deleteSel(){ if (ui.sel?.kind==='furn'){ const id = ui.sel.id; ui.sel = null; mutate(() => state.furniture = state.furniture.filter(f => f.id !== id)); } }
export function duplicateSel(){
  if (ui.sel?.kind !== 'furn') return;
  const f = getF(ui.sel.id), n = {...f, id:uid(), cx:f.cx+200, cy:f.cy+200};
  ui.sel = {kind:'furn', id:n.id}; mutate(() => state.furniture.push(n));
}
// 新放下的家具若压在墙 / 窗上，沿穿透较浅的方向推出来，刚好贴墙
export function pushOut(f){
  for (let n = 0; n < 4; n++){
    let moved = false;
    for (const r of snapRects()){
      const {hw, hh} = aabb(f), ox = Math.min(f.cx+hw, r[2]) - Math.max(f.cx-hw, r[0]), oy = Math.min(f.cy+hh, r[3]) - Math.max(f.cy-hh, r[1]);
      if (ox <= 0 || oy <= 0) continue;
      if (ox < oy) f.cx = f.cx < (r[0]+r[2])/2 ? r[0]-hw : r[2]+hw;
      else f.cy = f.cy < (r[1]+r[3])/2 ? r[1]-hh : r[3]+hh;
      moved = true;
    }
    if (!moved) return;
  }
}
export function addItem(it, x, y){
  const [type,name,w,d,color] = it, f = F(type,name,Math.round(x/10)*10,Math.round(y/10)*10,w,d,0,color);
  pushOut(f);
  ui.sel = {kind:'furn', id:f.id};
  mutate(() => type==='rug' ? state.furniture.unshift(f) : state.furniture.push(f));
  toast(tr(`已添加「${name}」${w}×${d}`, `Added "${nm(name)}" ${w}×${d}`));
}
function toggleWall(id){
  const w = WALLS[+id.slice(1)];
  if (w[4]==='b') return toast(tr('承重墙（黑色）不可拆除', 'Load-bearing walls (black) cannot be removed'));
  if (w[4]==='e') return toast(tr('外墙属于建筑外围护结构，不建议拆除', 'Exterior walls are part of the building envelope and should not be removed'));
  const on = state.demolished.includes(id);
  mutate(() => state.demolished = on ? state.demolished.filter(x => x!==id) : [...state.demolished, id]);
  toast(on ? tr('已恢复墙体', 'Wall restored') : tr(`已标记拆除 ${Math.max(w[2]-w[0], w[3]-w[1])} mm 墙体`, `Marked ${Math.max(w[2]-w[0], w[3]-w[1])} mm of wall for removal`));
}

export function setTool(t){
  ui.tool = t; ui.mA = null; ui.mCur = null;
  svg.setAttribute('class', 'tool-' + t);
  document.querySelectorAll('#tools .btn').forEach(b => b.classList.toggle('on', b.dataset.tool === t));
  syncModeHint();
  renderMeasure();
}
function syncModeHint(){
  const hints = {select:'',
    measure:COARSE ? tr('按住拖出测量线，或依次点两点 · 靠近墙面自动吸附 · 点「选择」退出', 'Hold and drag a line, or tap two points · snaps to walls · tap "Select" to exit')
      : tr('点击两点（或按住拖动）测量距离 · 靠近墙面自动吸附 · Shift 锁定水平/垂直 · Esc 取消', 'Click two points (or drag) to measure · snaps to walls · Shift locks horizontal/vertical · Esc cancels'),
    demolish:tr('点击灰色非承重墙标记拆除，再次点击恢复 · 黑色承重墙不可拆', 'Click a grey non-bearing wall to remove it, click again to restore · black bearing walls cannot be removed')};
  const h = $('#modehint'); h.textContent = hints[ui.tool]; h.classList.toggle('show', !!hints[ui.tool]);
}

/* ======================= 视图 ======================= */
export function applyView(){
  const W = svg.clientWidth, H = svg.clientHeight;
  svg.setAttribute('viewBox', `${view.x0} ${view.y0} ${W/view.s} ${H/view.s}`);
  const ratio = 1/(view.s*PX_MM);
  $('#ratio').textContent = '1:' + Math.round(ratio);
  const nice = [100,200,500,1000,2000,5000].find(v => v*view.s >= 60) || 5000;
  $('#sbBar').style.width = nice*view.s + 'px';
  $('#sbText').textContent = nice >= 1000 ? `${nice/1000} m` : `${nice} mm`;
  renderSel(); renderMeasure();
}
export function fitView(){
  const W = svg.clientWidth, H = svg.clientHeight;
  view.s = Math.min(W/BOUNDS.w, H/BOUNDS.h);
  view.x0 = BOUNDS.x - (W/view.s - BOUNDS.w)/2; view.y0 = BOUNDS.y - (H/view.s - BOUNDS.h)/2;
  applyView();
}
function zoomAt(ns, mx, my){
  ns = Math.max(.012, Math.min(2, ns));
  const px = view.x0 + mx/view.s, py = view.y0 + my/view.s;
  view.s = ns; view.x0 = px - mx/ns; view.y0 = py - my/ns; applyView();
}
export const zoomCenter = k => zoomAt(view.s*k, svg.clientWidth/2, svg.clientHeight/2);
export const setRatio = r => zoomAt(1/(r*PX_MM), svg.clientWidth/2, svg.clientHeight/2);

export function toMM(e){
  const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

/* ======================= 吸附 ======================= */
const grid = () => 10;
export function snapMove(f, cx, cy){
  let nx = Math.round(cx/grid())*grid(), ny = Math.round(cy/grid())*grid();
  if (!ui.layers.wallSnap) return [nx, ny];
  const {hw, hh} = aabb(f), tol = 10/view.s;
  let bx = tol, by = tol;
  for (const r of snapRects()){
    if (!(r[3] < cy-hh-tol || r[1] > cy+hh+tol)) for (const ex of [r[0], r[2]]) for (const c of [ex+hw, ex-hw]) if (Math.abs(c-cx) < bx){ bx = Math.abs(c-cx); nx = c; }
    if (!(r[2] < cx-hw-tol || r[0] > cx+hw+tol)) for (const ey of [r[1], r[3]]) for (const c of [ey+hh, ey-hh]) if (Math.abs(c-cy) < by){ by = Math.abs(c-cy); ny = c; }
  }
  return [nx, ny];
}
function snapPoint(p, shift){
  let x = Math.round(p.x/10)*10, y = Math.round(p.y/10)*10;
  const tol = 8/view.s; let bx = tol, by = tol;
  for (const r of snapRects()){
    for (const ex of [r[0], r[2]]) if (Math.abs(ex-p.x) < bx){ bx = Math.abs(ex-p.x); x = ex; }
    for (const ey of [r[1], r[3]]) if (Math.abs(ey-p.y) < by){ by = Math.abs(ey-p.y); y = ey; }
  }
  if (shift && ui.mA){ if (Math.abs(x-ui.mA.x) > Math.abs(y-ui.mA.y)) y = ui.mA.y; else x = ui.mA.x; }
  return {x, y};
}

/* ======================= 指针交互 ======================= */
let drag = null, pinch = null;
const touches = new Map();                     // 当前按在平面图上的手指
const svgXY = (x, y) => { const r = svg.getBoundingClientRect(); return [x - r.left, y - r.top]; };
function pinchInfo(){
  const [a, b] = [...touches.values()];
  return {d:Math.max(1, Math.hypot(b.x-a.x, b.y-a.y)), c:svgXY((a.x+b.x)/2, (a.y+b.y)/2)};
}
// 结束当前拖动：移动过的家具记入撤销栈
function endDrag(cancel){
  const d = drag; drag = null; svg.classList.remove('panning');
  if (!d) return;
  if (d.kind === 'measure'){
    if (cancel){ ui.mA = ui.mCur = null; renderMeasure(); return; }
    if (d.moved && ui.mA && ui.mCur && Math.hypot(ui.mCur.x-ui.mA.x, ui.mCur.y-ui.mA.y) > 20){
      const a = ui.mA, b = ui.mCur; ui.mA = ui.mCur = null; mutate(() => state.measures.push({a, b}));
    }
    renderMeasure(); return;                   // 没拖动：保留起点，等第二次点击
  }
  if (d.kind === 'pan'){
    if (!cancel && !d.moved && ui.tool === 'select') select(d.room ? {kind:'room', id:d.room} : null);
    return;
  }
  if (d.moved){ commit(d.before); renderAll(); }
}

svg.addEventListener('pointerdown', e => {
  if (e.button === 1 || e.button === 2) return;
  closeDrawers(); $('details.menu').open = false;
  if (e.pointerType !== 'mouse'){
    touches.set(e.pointerId, {x:e.clientX, y:e.clientY});
    svg.setPointerCapture(e.pointerId);
    if (touches.size >= 2){                    // 第二根手指落下：取消单指操作，进入双指缩放 / 平移
      endDrag(drag?.kind === 'measure' || drag?.kind === 'pan');
      const {d, c} = pinchInfo();
      pinch = {d, c, s:view.s, px:view.x0 + c[0]/view.s, py:view.y0 + c[1]/view.s};
      return;
    }
  }
  if (pinch) return;
  const p = toMM(e), t = e.target;
  if (ui.tool === 'measure'){
    const q = snapPoint(p, e.shiftKey);
    if (!ui.mA){ ui.mA = q; ui.mCur = q; drag = {kind:'measure', sx:e.clientX, sy:e.clientY, moved:false}; svg.setPointerCapture(e.pointerId); }
    else { const a = ui.mA; ui.mA = null; ui.mCur = null; if (Math.hypot(q.x-a.x, q.y-a.y) > 20) mutate(() => state.measures.push({a, b:q})); }
    renderMeasure(); return;
  }
  const h = t.closest('[data-handle]');
  if (h && ui.sel?.kind === 'furn'){
    drag = {kind:h.dataset.handle, id:ui.sel.id, sx:e.clientX, sy:e.clientY, before:snap(), moved:false};
  } else if (ui.tool === 'demolish' && t.closest('[data-wall]')){
    toggleWall(t.closest('[data-wall]').dataset.wall); return;
  } else if (ui.tool === 'select' && t.closest('[data-fid]')){
    const f = getF(t.closest('[data-fid]').dataset.fid);
    if (ui.sel?.id !== f.id) select({kind:'furn', id:f.id});
    drag = {kind:'move', id:f.id, sx:e.clientX, sy:e.clientY, ox:p.x-f.cx, oy:p.y-f.cy, before:snap(), moved:false};
  } else {
    const room = t.closest('[data-room]');
    drag = {kind:'pan', sx:e.clientX, sy:e.clientY, x0:view.x0, y0:view.y0, room:room && room.dataset.room, moved:false};
  }
  svg.setPointerCapture(e.pointerId);
});

svg.addEventListener('pointermove', e => {
  if (touches.has(e.pointerId)) touches.set(e.pointerId, {x:e.clientX, y:e.clientY});
  if (pinch){
    if (touches.size < 2) return;
    const {d, c} = pinchInfo(), ns = Math.max(.012, Math.min(2, pinch.s * d / pinch.d));
    view.s = ns; view.x0 = pinch.px - c[0]/ns; view.y0 = pinch.py - c[1]/ns; applyView();
    return;
  }
  const p = toMM(e);
  $('#cx').textContent = Math.round(p.x) + ' mm'; $('#cy').textContent = Math.round(p.y) + ' mm';
  if (!drag){
    const room = e.target.closest && e.target.closest('[data-room]');
    $('#hover').innerHTML = room ? `<b>${esc(state.rooms[room.dataset.room].name)}</b> ${fmt(area(ROOMS.find(r=>r.id===room.dataset.room).poly))} m²` : '';
    if (ui.tool === 'measure' && ui.mA){ ui.mCur = snapPoint(p, e.shiftKey); renderMeasure(); }
    return;
  }
  const far = Math.hypot(e.clientX-drag.sx, e.clientY-drag.sy) >= TAP;
  if (drag.kind === 'measure'){
    if (far) drag.moved = true;
    ui.mCur = snapPoint(p, e.shiftKey); renderMeasure(); return;
  }
  if (drag.kind === 'pan'){
    if (!drag.moved && !far) return;
    drag.moved = true; svg.classList.add('panning');
    view.x0 = drag.x0 - (e.clientX-drag.sx)/view.s; view.y0 = drag.y0 - (e.clientY-drag.sy)/view.s; applyView(); return;
  }
  const f = getF(drag.id); if (!f) return;
  if (!drag.moved && !far) return;             // 轻点家具不应让它抖动一下
  drag.moved = true;
  if (drag.kind === 'move'){
    [f.cx, f.cy] = snapMove(f, p.x-drag.ox, p.y-drag.oy);
  } else if (drag.kind === 'rot'){
    let a = Math.atan2(p.y-f.cy, p.x-f.cx)*180/Math.PI + 90;
    f.rot = norm(e.shiftKey ? a : Math.round(a/15)*15);
  } else if (drag.kind === 'size'){
    const a = f.rot*Math.PI/180, c = Math.cos(a), s = Math.sin(a);
    const dx = p.x-f.cx, dy = p.y-f.cy, lx = dx*c + dy*s, ly = -dx*s + dy*c;
    const ax = -f.w/2, ay = -f.d/2;
    const nw = Math.max(100, Math.round((lx-ax)/10)*10), nd = Math.max(100, Math.round((ly-ay)/10)*10);
    const mx = ax + nw/2, my = ay + nd/2;
    f.cx += mx*c - my*s; f.cy += mx*s + my*c; f.w = nw; f.d = nd;
  }
  renderFurn(); renderSel();
});

function onPointerEnd(e){
  touches.delete(e.pointerId);
  if (pinch){ if (touches.size < 2) pinch = null; return; }   // 双指结束后，剩下的手指不再触发操作
  endDrag(e.type === 'pointercancel');
}
svg.addEventListener('pointerup', onPointerEnd);
svg.addEventListener('pointercancel', onPointerEnd);
// 阻止 iPad Safari 把双指手势当成整页缩放
['gesturestart','gesturechange','gestureend'].forEach(t => document.addEventListener(t, e => e.preventDefault()));

svg.addEventListener('wheel', e => {
  e.preventDefault();
  const r = svg.getBoundingClientRect();
  zoomAt(view.s*Math.exp(-e.deltaY*(e.ctrlKey ? .01 : .0015)), e.clientX-r.left, e.clientY-r.top);
}, {passive:false});
svg.addEventListener('dblclick', e => { if (ui.tool==='select' && e.target.closest('[data-fid]')) rotateSel(90); });
svg.addEventListener('contextmenu', e => { if (ui.tool==='measure'){ e.preventDefault(); ui.mA = null; renderMeasure(); } });


/* ======================= 键盘 ======================= */
document.addEventListener('keydown', e => {
  if (e.target.matches('input,select,textarea')) return;
  if (window.View3D?.walking()) return;
  const mod = e.metaKey || e.ctrlKey, k = e.key.toLowerCase();
  if (mod && k === 'z'){ e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
  if (mod && k === 'y'){ e.preventDefault(); redo(); return; }
  if (mod && k === 'd'){ e.preventDefault(); duplicateSel(); return; }
  if (mod) return;
  if (k === '[' || k === ']'){ drawer(k === '[' ? 'lib' : 'panel'); return; }
  if (k === 'f' && e.shiftKey){ toggleFullscreen(); return; }
  if (k === 't') setView(is3D() ? '2d' : '3d');
  else if (is3D() && ['v','m','x','f','+','=','-'].includes(k)) return;
  else if (k === 'v') setTool('select');
  else if (k === 'm') setTool('measure');
  else if (k === 'x') setTool('demolish');
  else if (k === 'f') fitView();
  else if (k === 'r') rotateSel(e.shiftKey ? -90 : 90);
  else if (k === 'delete' || k === 'backspace'){ e.preventDefault(); deleteSel(); }
  else if (k === 'escape'){ if (ui.mA){ ui.mA = null; renderMeasure(); } else { if (ui.tool !== 'select') setTool('select'); select(null); } }
  else if (k.startsWith('arrow') && ui.sel?.kind === 'furn'){
    e.preventDefault(); const st = e.shiftKey ? 100 : 10;
    mutate(() => { const f = getF(ui.sel.id); if (k==='arrowleft') f.cx -= st; if (k==='arrowright') f.cx += st; if (k==='arrowup') f.cy -= st; if (k==='arrowdown') f.cy += st; });
  }
  else if (k === '+' || k === '=') zoomCenter(1.25);
  else if (k === '-') zoomCenter(.8);
});


window.select = select;
window.snapMove = snapMove;
window.getF = getF;
window.snap = snap;
window.commit = commit;
window.renderAll = renderAll;
