// UI Sidebar Panels (Room Properties, Furniture Parameters, Overview Stats)
import { $, $$, COARSE, esc, fmt, norm, area, perim, bbox, narrow, PANES_KEY, toast } from '../config.js';
import { tr, nm } from '../i18n.js';
import { ROOMS, WALLS } from '../data/floorplan.js';
import { MATS, WALL_PAINTS } from '../data/materials.js';
import { SOCKET_TYPES, SOCKET_HEIGHTS, calculateSocketSchedule, autoGenerateSockets } from '../data/electrical.js';
import { openElectricalPrintSheet } from './electrical-print.js';
import { state, ui, getF, mutate, snap, commit } from '../2d/state.js';
import { select, rotateSel, duplicateSel, deleteSel } from '../2d/interactions.js';
import { is3D } from './toolbar.js';

/* ======================= Properties Panel ======================= */

export function renderPanel(){
  renderFab();
  const p = $('#panel');
  if (ui.sel?.kind === 'socket'){
    const sk = state.sockets?.find(s => s.id === ui.sel.id);
    if (sk){ p.innerHTML = socketPanel(sk); bindSocketPanel(sk); return; }
  }
  if (ui.sel?.kind === 'furn'){ const f = getF(ui.sel.id); if (f){ p.innerHTML = furnPanel(f); bindFurnPanel(f); return; } }
  if (ui.sel?.kind === 'room'){ const r = ROOMS.find(r => r.id === ui.sel.id); if (r){ p.innerHTML = roomPanel(r); bindRoomPanel(); return; } }
  if (ui.viewMode === 'elec'){ p.innerHTML = electricalOverviewPanel(); bindElectricalOverview(); return; }
  p.innerHTML = overviewPanel(); bindOverview();
}

export function overviewPanel(){
  const rows = ROOMS.map(r => {
    const st = state.rooms[r.id];
    const matSw = MATS[st?.mat]?.sw || '#d8c2a2';
    return `<tr class="click" data-room="${r.id}"><td><span class="sw" style="background:${matSw}"></span>${esc(nm(st?.name || r.name))}${r.counted===false?' <span class="muted">*</span>':''}</td>
      <td class="r">${fmt(area(r.poly))} m²</td></tr>`;
  }).join('');
  const tot = ROOMS.filter(r => r.counted !== false).reduce((a,r) => a + area(r.poly), 0);
  const byMat = {};
  ROOMS.forEach(r => { const m = state.rooms[r.id].mat; byMat[m] = (byMat[m]||0) + area(r.poly); });
  let cost = 0;
  const matRows = Object.entries(byMat).map(([m,a]) => { const c = a*MATS[m].price*1.05; cost += c;
    return `<tr><td><span class="sw" style="background:${MATS[m].sw}"></span>${nm(MATS[m].name)}</td><td class="r">${fmt(a,1)} m²</td><td class="r">${Math.round(c).toLocaleString()} ر.س</td></tr>`; }).join('');

  const byPaint = {};
  ROOMS.forEach(r => {
    if (r.counted === false) return;
    const pm = state.rooms[r.id]?.wallMat || 'alabaster';
    const wa = perim(r.poly) * 2.8;
    byPaint[pm] = (byPaint[pm] || 0) + wa;
  });
  let paintCost = 0;
  const paintRows = Object.entries(byPaint).map(([m, a]) => {
    const p = WALL_PAINTS[m] || WALL_PAINTS.alabaster;
    const c = a * p.price;
    paintCost += c;
    return `<tr><td><span class="sw" style="background:${p.sw}"></span>${nm(p.name)}</td><td class="r">${fmt(a,1)} m²</td><td class="r">${Math.round(c).toLocaleString()} ر.س</td></tr>`;
  }).join('');

  const dem = state.demolished.map(id => WALLS[+id.slice(1)]);
  const demLen = dem.reduce((a,w) => a + Math.max(w[2]-w[0], w[3]-w[1]), 0) / 1000;
  return `
  <section><h3>${tr('مساحات الغرف','Room Areas')} <small>${tr('اضغط للاستعراض وتغيير الأرضيات والدهانات','Click to view / change materials')}</small></h3>
    <table>${rows}</table>
    <div class="total"><span>${tr('المساحة الصافية الإجمالية','Net floor area')}</span><b>${fmt(tot)} m²</b></div>
    <div class="muted" style="font-size:11px;margin-top:4px">${tr('* المساحات محسوبة بدقة من الأوجه الداخلية الصافية للجدران','* Areas calculated using net inner wall dimensions')}</div></section>
  <section><h3>${tr('تقدير كميات وتكلفة الأرضيات','Flooring Estimate')} <small>${tr('شامل 5% نسبة هالك','incl. 5% waste')}</small></h3>
    <table>${matRows}</table>
    <div class="total"><span>${tr('إجمالي تكلفة الأرضيات','Flooring total')}</span><b>${Math.round(cost).toLocaleString()} ر.س</b></div></section>
  <section><h3>${tr('تقدير كميات وتكلفة دهانات الجدران','Wall Paint Estimate')} <small>${tr('ارتفاع 2.8 م','2.8m height')}</small></h3>
    <table>${paintRows}</table>
    <div class="total"><span>${tr('إجمالي تكلفة الدهانات','Wall paint total')}</span><b>${Math.round(paintCost).toLocaleString()} ر.س</b></div></section>
  <section><h3>${tr('إحصائيات المخطط','Plan Stats')}</h3>
    <div class="stats"><div><small>${tr('عدد قطع الأثاث','Furniture')}</small><span class="big">${state.furniture.length}</span></div>
      <div><small>${tr('الجدران المعدلة','Walls removed')}</small><span class="big">${fmt(demLen,1)}</span> m</div></div>
    <div class="actions"><button class="btn" id="clearMeasure">${tr('مسح خطوط القياس','Clear measures')} (${state.measures.length})</button>
      <button class="btn danger" id="clearFurn">${tr('إفراغ التأثيث','Clear layout')}</button></div></section>
  ${COARSE ? tr(`<section><h3>إيماءات شاشة اللمس</h3><div class="kbd">
    <kbd>سحب بإصبع واحد</kbd><span>تحريك الكاميرا والمشهد</span><kbd>إصبعين</kbd><span>تقريب / تصغير وتحريك</span>
    <kbd>مكتبة الأثاث</kbd><span>اضغط للإضافة في المركز، أو اسحب للموضع المطلوب</span>
    <kbd>تحديد قطعة</kbd><span>اسحب للتحريك؛ النقطة العلوية للتدوير والمربع لتعديل الحجم</span>
    <kbd>شريط الأدوات</kbd><span>أزرار سريعة للتدوير والنسخ والحذف</span>
    <kbd>أداة القياس</kbd><span>اسحب لرسم خط قياس أو انقر نقطتين</span>
    <kbd>جولة 3D</kbd><span>عصا التحكم السفلية للحركة، اسحب للنظر حولك، انقر على الأبواب لفتحها</span>
  </div></section>`, `<section><h3>Touch Controls</h3><div class="kbd">
    <kbd>1-finger drag</kbd><span>Pan on empty space</span><kbd>2 fingers</kbd><span>Pinch to zoom, drag to pan</span>
    <kbd>Library</kbd><span>Tap to place at center, or hold and drag right to a spot</span>
    <kbd>Tap item</kbd><span>Drag to move; top dot rotates, bottom-right square resizes</span>
    <kbd>Toolbar</kbd><span>Bottom bar can rotate / duplicate / delete</span>
    <kbd>Measure</kbd><span>Hold and drag a line, or tap two points</span>
    <kbd>3D walk</kbd><span>Joystick moves, drag to look, tap doors to open</span>
  </div></section>`) : ''}
  ${tr(`<section><h3>اختصارات لوحة المفاتيح</h3><div class="kbd">
    <kbd>سحب وإفلات</kbd><span>سحب الأثاث من القائمة إلى المخطط</span><kbd>V</kbd><span>تحديد / تحريك</span><kbd>M</kbd><span>قياس الأبعاد</span>
    <kbd>X</kbd><span>تعديل الجدران غير الإنشائية</span><kbd>R</kbd><span>تدوير 90 درجة</span><kbd>الأسهم</kbd><span>تحريك دقيق 10 مم</span>
    <kbd>Ctrl + D</kbd><span>تكرار ونسخ</span><kbd>Delete</kbd><span>حذف القطعة</span><kbd>Ctrl + Z</kbd><span>تراجع</span><kbd>T</kbd><span>تبديل 2D / 3D</span><kbd>F</kbd><span>ملاءمة الشاشة</span><kbd>Esc</kbd><span>إلغاء التحديد</span>
  </div></section>`, `<section><h3>Keyboard Shortcuts</h3><div class="kbd">
    <kbd>Drag</kbd><span>Drag furniture onto the plan</span><kbd>V</kbd><span>Select / move</span><kbd>M</kbd><span>Measure (Shift: horizontal/vertical)</span>
    <kbd>X</kbd><span>Demolish non-bearing walls (black = bearing)</span><kbd>R</kbd><span>Rotate 90° (Shift reverses)</span><kbd>Arrows</kbd><span>Nudge 10mm (Shift 100mm)</span>
    <kbd>⌘/Ctrl D</kbd><span>Duplicate</span><kbd>Delete</kbd><span>Delete</span><kbd>⌘/Ctrl Z</kbd><span>Undo</span><kbd>T</kbd><span>Toggle 2D / 3D</span><kbd>F</kbd><span>Fit to window</span><kbd>Esc</kbd><span>Deselect</span>
  </div></section>`)}`;
}
export function bindOverview(){
  document.querySelectorAll('#panel tr[data-room]').forEach(tr => tr.onclick = () => { select({kind:'room', id:tr.dataset.room}); if (is3D()) window.View3D.flyToRoom(tr.dataset.room); });
  $('#clearMeasure').onclick = () => state.measures.length && mutate(() => state.measures = []);
  $('#clearFurn').onclick = clearLayout;
}

// Floating Action Bar (Touch / Mobile Quick Actions: Rotate, Duplicate, Delete, Floor Properties)
export function renderFab(){
  const fab = $('#fab');
  const sk = ui.sel?.kind === 'socket' && state.sockets?.find(s => s.id === ui.sel.id);
  const f = ui.sel?.kind === 'furn' && getF(ui.sel.id);
  const r = ui.sel?.kind === 'room' && ROOMS.find(r => r.id === ui.sel.id);

  if (!sk && !f && !r){ fab.classList.remove('show'); return; }

  if (sk) {
    const meta = SOCKET_TYPES[sk.type] || SOCKET_TYPES.duplex;
    fab.innerHTML = `
      <span class="name">${meta.icon} ${meta.name.zh} <small style="background:#0f172a;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px">${sk.height}</small></span>
      <button class="btn danger" data-a="delSk">${tr('حذف','Delete')}</button>
      <button class="btn primary" data-a="prop">${tr('الخصائص','Properties')}</button>
      <button class="btn" data-a="done">${tr('تم','Done')}</button>
    `;
    fab.classList.add('show');
    fab.querySelectorAll('[data-a]').forEach(b => b.onclick = () => ({
      delSk: deleteSel,
      prop: () => drawer('panel', true),
      done: () => { select(null); closeDrawers(); }
    })[b.dataset.a]());
    return;
  }

  fab.innerHTML = f
    ? `<span class="name">${esc(nm(f.name))}</span><button class="btn" data-a="rotL">↺</button><button class="btn" data-a="rotR">↻ ${tr('تدوير','Rotate')}</button>
       <button class="btn" data-a="dup">${tr('نسخ','Duplicate')}</button><button class="btn danger" data-a="del">${tr('حذف','Delete')}</button><span class="sep"></span>
       <button class="btn" data-a="prop">${tr('الخصائص','Properties')}</button><button class="btn" data-a="done">${tr('تم','Done')}</button>`
    : `<span class="name">${esc(nm(state.rooms[r.id].name))}</span><button class="btn primary" data-a="prop">🎨 ${tr('الأرضية / الخصائص','Floor / Properties')}</button><button class="btn" data-a="done">${tr('تم','Done')}</button>`;
  fab.classList.add('show');
  fab.querySelectorAll('[data-a]').forEach(b => b.onclick = () => ({
    rotL:() => rotateSel(-90), rotR:() => rotateSel(90), dup:duplicateSel, del:deleteSel,
    prop:() => drawer('panel', true), done:() => { select(null); closeDrawers(); },
  })[b.dataset.a]());
}

export function clearLayout(){
  const n = state.furniture.length;
  if (!n) return toast(tr('لا يوجد أثاث حالياً لإفراغه', 'There is no furniture to clear'));
  if (!confirm(tr(`هل أنت متأكد من حذف كافة قطع الأثاث والأجهزة (${n} قطعة)؟\nسيتم الاحتفاظ بالجدران والأرضيات والقياسات، ويمكنك التراجع لاحقاً.`, `Remove all ${n} furniture / appliance items?\nWalls, flooring and measurements are kept. You can Undo this.`))) return;
  ui.sel = null; mutate(() => state.furniture = []);
  toast(tr('تم إفراغ التأثيث، يمكنك الضغط على «تراجع» للاستعادة', 'Layout cleared — Undo to restore'));
}

/* Sidebar Drawer Management: which = 'lib' | 'panel' | null */
const PANES = 'huxing-panes';
const panes = (() => { try { return JSON.parse(localStorage.getItem(PANES)) || {}; } catch(e) { return {}; } })();
export function drawer(which, open){
  const app = $('.app'), els = {lib:$('aside.lib'), panel:$('aside.right')}, n = narrow();
  if (n){
    Object.entries(els).forEach(([k, el]) => el.classList.toggle('open', k === which && (open ?? !el.classList.contains('open'))));
  } else {
    Object.values(els).forEach(el => el.classList.remove('open'));
    if (which){
      const k = which === 'lib' ? 'hideLib' : 'hidePanel';
      panes[k] = open === undefined ? !panes[k] : !open;
      try { localStorage.setItem(PANES, JSON.stringify(panes)); } catch(e) {}
    }
  }
  app.classList.toggle('hide-lib', !!panes.hideLib); app.classList.toggle('hide-panel', !!panes.hidePanel);
  syncPaneBtns();
}
export function syncPaneBtns(){
  const els = {lib:$('aside.lib'), panel:$('aside.right')}, n = narrow();
  const vis = k => n ? els[k].classList.contains('open') : !panes[k === 'lib' ? 'hideLib' : 'hidePanel'];
  $('#tgLib').classList.toggle('on', vis('lib')); $('#tgPanel').classList.toggle('on', vis('panel'));
  $('#tgLib').title = vis('lib') ? tr('إخفاء مكتبة الأثاث ( [ )', 'Hide library ( [ )') : tr('عرض مكتبة الأثاث ( [ )', 'Show library ( [ )');
  $('#tgPanel').title = vis('panel') ? tr('إخفاء لوحة الخصائص ( ] )', 'Hide properties ( ] )') : tr('عرض لوحة الخصائص ( ] )', 'Show properties ( ] )');
  $('#stage').classList.toggle('drawer-panel', n && vis('panel'));
}
export function closeDrawers(){ if (narrow()) drawer(null); }

export function roomPanel(r){
  const st = state.rooms[r.id], a = area(r.poly), [x0,y0,x1,y1] = bbox(r.poly), inside = state.furniture.filter(f => f.cx>x0&&f.cx<x1&&f.cy>y0&&f.cy<y1);
  const mats = Object.entries(MATS).map(([k,m]) => `<button class="mat ${k===st.mat?'on':''}" data-mat="${k}"><i style="background:${m.sw}"></i><span>${nm(m.name)}<small>${m.price} ر.س / م²</small></span></button>`).join('');

  const curWallMat = st.wallMat || 'alabaster';
  const wallArea = perim(r.poly) * 2.8;
  const curPaint = WALL_PAINTS[curWallMat] || WALL_PAINTS.alabaster;
  const wallCost = Math.round(wallArea * curPaint.price);

  const paintGroups = [
    { id: 'ksa', label: tr('🇸🇦 طراز وتراث سعودي وإقليمي', '🇸🇦 KSA & Regional Heritage') },
    { id: 'texture', label: tr('✨ شرائح خشبية وخامات جدارية فاخرة', '✨ Wall Slats & Luxury Textures') },
    { id: 'paint', label: tr('🎨 دهانات معمارية ومودرن', '🎨 Minimalist Architectural Paints') }
  ];

  const paints = paintGroups.map(grp => {
    const items = Object.entries(WALL_PAINTS).filter(([k, p]) => (p.category || 'paint') === grp.id);
    if (!items.length) return '';
    const btns = items.map(([k, p]) => `<button class="mat ${k===curWallMat?'on':''}" data-paint="${k}"><i style="background:${p.sw};${p.hasTexture?'box-shadow:inset 0 0 0 1px rgba(0,0,0,0.18)':''}"></i><span>${nm(p.name)}<small>${p.price} ر.س / م²</small></span></button>`).join('');
    return `<div class="mat-group" style="margin-bottom:8px"><div class="group-title" style="font-size:11.5px;font-weight:700;color:var(--text-muted);margin:6px 0 4px 0">${grp.label}</div><div class="mats">${btns}</div></div>`;
  }).join('');

  return `<section><h3>${tr('الغرفة','Room')}</h3>
    <div class="form"><label class="full">${tr('اسم الغرفة','Name')}<input id="rName" value="${esc(nm(st.name))}"></label></div>
    <div class="stats" style="margin-top:10px">
      <div><small>${tr('المساحة الصافية','Floor area')}</small><span class="big">${fmt(a)}</span> m²</div>
      <div><small>${tr('المحيط','Perimeter')}</small><span class="big">${fmt(perim(r.poly),1)}</span> m</div>
      <div><small>${tr('العرض','Width')}</small><span class="big">${x1-x0}</span> mm</div>
      <div><small>${tr('العمق','Depth')}</small><span class="big">${y1-y0}</span> mm</div></div>
    <div class="muted">${tr(`مساحة الجدران (ارتفاع 2.8 م، بدون خصم الفتحات) تقريباً ${fmt(wallArea,1)} م²`, `Wall area (2.8m ceiling, openings not deducted) ≈ ${fmt(wallArea,1)} m²`)}</div></section>
  <section><h3>${tr('نوع وتشطيب الأرضية','Flooring Material')}</h3><div class="mats">${mats}</div>
    <div class="total"><span>${tr('تقدير تكلفة الأرضيات','Flooring estimate')}</span><b>${Math.round(a*MATS[st.mat].price*1.05).toLocaleString()} ر.س</b></div></section>
  <section><h3>${tr('تشطيب ودهان الجدران','Wall Paint & Textures')}</h3>
    ${paints}
    ${curPaint.desc ? `<div class="muted" style="margin-top:6px;font-size:11px;line-height:1.4;background:rgba(0,0,0,0.03);padding:6px 8px;border-radius:6px">💡 ${curPaint.desc}</div>` : ''}
    <div class="total" style="margin-top:8px"><span>${tr('تقدير تكلفة الجدران (ارتفاع 2.8 م)','Wall finish estimate (2.8m)')}</span><b>${wallCost.toLocaleString()} ر.س</b></div></section>
  <section><h3>${tr('الأثاث داخل الغرفة','Furniture in room')} <small>${tr(`${inside.length} قطعة`, `${inside.length} items`)}</small></h3>
    <table>${inside.map(f => `<tr class="click" data-fid="${f.id}"><td>${esc(nm(f.name))}</td><td class="r muted">${f.w}×${f.d}</td></tr>`).join('') || `<tr><td class="muted">${tr('لا يوجد أثاث','None')}</td></tr>`}</table>
    <div class="actions"><button class="btn" id="back">${tr('← العودة للملخص','← Back to overview')}</button></div></section>`;
}
export function bindRoomPanel(){
  const id = ui.sel?.id;
  if (!id || !state.rooms[id]) return;
  const rName = $('#rName');
  if (rName) rName.onchange = e => mutate(() => state.rooms[id].name = e.target.value.trim() || state.rooms[id].name);
  document.querySelectorAll('#panel [data-mat]').forEach(b => b.onclick = (e) => {
    e.stopPropagation();
    const newMat = b.dataset.mat;
    mutate(() => {
      state.rooms[id].mat = newMat;
    });
    renderPanel();
    if (is3D() && window.View3D?.sync) {
      window.View3D.sync();
    }
    toast(tr(`تم تطبيق أرضية ${nm(MATS[newMat].name)} على ${nm(state.rooms[id].name)}`, `Applied ${nm(MATS[newMat].name)} flooring to ${nm(state.rooms[id].name)}`));
  });
  document.querySelectorAll('#panel [data-paint]').forEach(b => b.onclick = (e) => {
    e.stopPropagation();
    const newPaint = b.dataset.paint;
    mutate(() => {
      state.rooms[id].wallMat = newPaint;
    });
    renderPanel();
    if (is3D() && window.View3D?.sync) {
      window.View3D.sync();
    }
    toast(tr(`تم تطبيق دهان ${nm(WALL_PAINTS[newPaint].name)} على جدران ${nm(state.rooms[id].name)}`, `Applied ${nm(WALL_PAINTS[newPaint].name)} wall paint to ${nm(state.rooms[id].name)}`));
  });
  document.querySelectorAll('#panel tr[data-fid]').forEach(tr => tr.onclick = () => select({kind:'furn', id:tr.dataset.fid}));
  const backBtn = $('#back');
  if (backBtn) backBtn.onclick = () => select(null);
}

export function furnPanel(f){
  return `<section><h3>${tr('خصائص القطعة','Furniture')}</h3>
    <div class="form">
      <label class="full">${tr('اسم القطعة','Name')}<input id="fName" value="${esc(nm(f.name))}"></label>
      <label>${tr('العرض','Width')} (mm)<input type="number" id="fW" value="${f.w}" min="50" step="10"></label>
      <label>${tr('العمق','Depth')} (mm)<input type="number" id="fD" value="${f.d}" min="50" step="10"></label>
      <label>${tr('الموضع','Center')} X (mm)<input type="number" id="fX" value="${Math.round(f.cx)}" step="10"></label>
      <label>${tr('الموضع','Center')} Y (mm)<input type="number" id="fY" value="${Math.round(f.cy)}" step="10"></label>
      <label>${tr('الزاوية','Rotation')} (°)<input type="number" id="fR" value="${f.rot}" step="15"></label>
      <label>${tr('اللون','Color')}<input type="color" id="fC" value="${f.color}"></label>
    </div>
    <div class="muted" style="margin-top:8px">${tr('المساحة المشغولة','Footprint')} ${fmt(f.w*f.d/1e6)} م²</div>
    <div class="actions">
      <button class="btn" id="aRot">${tr('تدوير 90°','Rotate 90°')}</button><button class="btn" id="aDup">${tr('نسخ','Duplicate')}</button>
      <button class="btn" id="aTop">${tr('إلى الأمام','Bring to front')}</button><button class="btn" id="aBot">${tr('إلى الخلف','Send to back')}</button>
      <button class="btn danger" id="aDel">${tr('حذف','Delete')}</button><button class="btn" id="back">${tr('← عودة','← Back')}</button>
    </div></section>
  <section class="muted" style="font-size:12px">${tr('اسحب القطعة للتحريك، الدائرة العلوية للتدوير، والمربع بالزاوية السفلية لتعديل الأبعاد. تفعيل «محاذاة الجدران» يضمن الالتصاق التلقائي بالجدار.', 'Drag to move; drag the top dot to rotate; drag the bottom-right square to resize. With "Wall snap" on, items snap flush to nearby walls.')}</section>`;
}
export function bindFurnPanel(f){
  const upd = (fn) => mutate(() => { const g = getF(f.id); if (g) fn(g); });
  const num = (id, fn) => $(id).onchange = e => { const v = parseFloat(e.target.value); if (!isNaN(v)) upd(g => fn(g, v)); };
  $('#fName').onchange = e => upd(g => g.name = e.target.value.trim() || g.name);
  num('#fW', (g,v) => g.w = Math.max(50, Math.round(v)));
  num('#fD', (g,v) => g.d = Math.max(50, Math.round(v)));
  num('#fX', (g,v) => g.cx = v); num('#fY', (g,v) => g.cy = v); num('#fR', (g,v) => g.rot = norm(v));
  $('#fC').onchange = e => upd(g => g.color = e.target.value);
  $('#aRot').onclick = () => rotateSel(90);
  $('#aDup').onclick = duplicateSel;
  $('#aDel').onclick = deleteSel;
  $('#aTop').onclick = () => mutate(() => { const i = state.furniture.findIndex(g => g.id===f.id); state.furniture.push(...state.furniture.splice(i,1)); });
  $('#aBot').onclick = () => mutate(() => { const i = state.furniture.findIndex(g => g.id===f.id); state.furniture.unshift(...state.furniture.splice(i,1)); });
  $('#back').onclick = () => select(null);
}

/* ======================= Electrical Socket Panels ======================= */

export function socketPanel(sk) {
  const meta = SOCKET_TYPES[sk.type] || SOCKET_TYPES.duplex;
  const typeOpts = Object.values(SOCKET_TYPES).map(t =>
    `<option value="${t.id}" ${t.id === sk.type ? 'selected' : ''}>${t.icon} ${t.name.zh}</option>`
  ).join('');

  const heightOpts = SOCKET_HEIGHTS.map(h =>
    `<option value="${h.value}" ${h.value === sk.height ? 'selected' : ''}>${h.label.zh}</option>`
  ).join('');

  const r = ROOMS.find(rm => rm.id === sk.roomId);

  return `
    <section>
      <h3>⚡ ${tr('خصائص المقبس والتجهيز الكهربائي', 'Electrical Socket Properties')}</h3>
      <div class="form">
        <label class="full">${tr('نوع المقبس', 'Socket Type')}
          <select id="skType" style="width:100%;padding:7px;border-radius:6px;border:1px solid var(--line);font-family:inherit;font-size:12px;background:#fff">
            ${typeOpts}
          </select>
        </label>
        <label class="full">${tr('الارتفاع عن البلاط (AFF)', 'Mounting Height (AFF)')}
          <select id="skHeight" style="width:100%;padding:7px;border-radius:6px;border:1px solid var(--line);font-family:inherit;font-size:12px;background:#fff">
            ${heightOpts}
          </select>
        </label>
        <label class="full">${tr('التسمية والملاحظة', 'Label / Note')}
          <input id="skLabel" value="${esc(sk.label || '')}" placeholder="${tr('مثال: شاشة الصالون', 'e.g. Living Room TV')}">
        </label>
        <label>${tr('الموضع X', 'Pos X')}<input type="number" id="skX" value="${Math.round(sk.x)}" step="10"></label>
        <label>${tr('الموضع Y', 'Pos Y')}<input type="number" id="skY" value="${Math.round(sk.y)}" step="10"></label>
      </div>

      <div class="card-desc" style="margin-top:10px;padding:9px;background:rgba(2,132,199,0.07);border:1px solid rgba(2,132,199,0.2);border-radius:6px;font-size:11.5px;line-height:1.45">
        <b style="color:#0284c7">${meta.name.zh}:</b> ${meta.desc.zh}
        ${r ? `<div style="margin-top:5px;color:var(--text-muted);font-weight:600">📍 ${tr('الغرفة:', 'Room:')} ${esc(nm(r.name))}</div>` : ''}
      </div>

      <div class="actions" style="margin-top:12px">
        <button class="btn danger" id="skDel">🗑️ ${tr('حذف المخرج', 'Delete Socket')}</button>
        <button class="btn" id="skBack">${tr('← عودة', '← Back')}</button>
      </div>
    </section>
  `;
}

export function bindSocketPanel(sk) {
  const upd = (fn) => mutate(() => {
    const s = state.sockets?.find(x => x.id === sk.id);
    if (s) fn(s);
  });

  const skType = $('#skType');
  if (skType) skType.onchange = e => upd(s => {
    s.type = e.target.value;
    s.height = SOCKET_TYPES[s.type]?.defaultHeight || s.height;
    renderPanel();
  });

  const skHeight = $('#skHeight');
  if (skHeight) skHeight.onchange = e => upd(s => s.height = e.target.value);

  const skLabel = $('#skLabel');
  if (skLabel) skLabel.onchange = e => upd(s => s.label = e.target.value.trim());

  const num = (id, fn) => {
    const el = $(id);
    if (el) el.onchange = e => { const v = parseFloat(e.target.value); if (!isNaN(v)) upd(s => fn(s, v)); };
  };
  num('#skX', (s, v) => s.x = Math.round(v));
  num('#skY', (s, v) => s.y = Math.round(v));

  const skDel = $('#skDel');
  if (skDel) skDel.onclick = deleteSel;

  const skBack = $('#skBack');
  if (skBack) skBack.onclick = () => select(null);
}

export function electricalOverviewPanel() {
  const schedule = calculateSocketSchedule(state.sockets || [], ROOMS);
  const typeCards = Object.entries(SOCKET_TYPES).map(([k, t]) => {
    const cnt = schedule.byType[k] || 0;
    return `
      <div class="stat-mini-card" style="display:flex;align-items:center;gap:7px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:#fff">
        <span style="font-size:16px">${t.icon}</span>
        <div style="flex:1;min-width:0">
          <div style="font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${t.name.zh}</div>
          <div style="font-size:9.5px;color:var(--text-muted)">${t.defaultHeight}</div>
        </div>
        <b style="font-size:13px;color:${t.color}">${cnt}</b>
      </div>
    `;
  }).join('');

  const roomRows = Object.entries(schedule.byRoom).map(([rName, c]) => `
    <tr>
      <td>${esc(rName)}</td>
      <td class="r"><b>${c.total}</b> <small class="muted">مقبس</small></td>
    </tr>
  `).join('');

  return `
    <section>
      <h3>⚡ ${tr('مخطط وتوزيع الأفياش الكهربائية', 'Electrical Sockets Layout')}</h3>
      <div style="font-size:11.5px;color:var(--text-muted);margin-bottom:10px;line-height:1.4">
        ${tr('توزيع ذكي للمقابس بناءً على أماكن الأثاث والتجهيزات، مع التصدير والطباعة الهندسية.', 'Smart socket placement determined by furniture positions, with printable sheet & PDF export.')}
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px">
        <button class="btn primary" id="btnAutoElec" style="justify-content:center;padding:8px 4px;font-weight:700;font-size:11.5px">
          ⚡ ${tr('توليد حسب الأثاث', 'Auto-Generate')}
        </button>
        <button class="btn" id="btnPrintElec" style="justify-content:center;padding:8px 4px;background:#0f172a;color:#fff;border-color:#0f172a;font-weight:700;font-size:11.5px">
          🖨️ ${tr('طباعة وتصدير PDF', 'Print / PDF')}
        </button>
      </div>

      <div class="total" style="margin-bottom:10px">
        <span>${tr('إجمالي المقابس بالمسطح', 'Total Sockets')}</span>
        <b style="color:var(--accent);font-size:16px">${schedule.total} مقبس</b>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:12px">
        ${typeCards}
      </div>
    </section>

    <section>
      <h3>${tr('توزيع المقابس حسب الغرف', 'Sockets Per Room')}</h3>
      <table>${roomRows || `<tr><td class="muted">${tr('لا توجد مقابس حالياً','No sockets yet')}</td></tr>`}</table>
      <div class="actions" style="margin-top:12px">
        <button class="btn danger" id="btnClearElec">🗑️ ${tr('إفراغ الأفياش', 'Clear Sockets')}</button>
      </div>
    </section>
  `;
}

export function bindElectricalOverview() {
  const btnAuto = $('#btnAutoElec');
  if (btnAuto) {
    btnAuto.onclick = () => {
      mutate(() => {
        state.sockets = autoGenerateSockets(state.furniture, ROOMS, WALLS);
      });
      toast(tr(`تم توليد ${state.sockets.length} مقبس كهربائي بنجاح متوافقة مع الأثاث`, `Generated ${state.sockets.length} sockets matching furniture`));
      renderPanel();
    };
  }

  const btnPrint = $('#btnPrintElec');
  if (btnPrint) {
    btnPrint.onclick = () => openElectricalPrintSheet();
  }

  const btnClear = $('#btnClearElec');
  if (btnClear) {
    btnClear.onclick = () => {
      if (!state.sockets?.length) return;
      if (!confirm(tr('هل أنت متأكد من مسح جميع الأفياش من المخطط؟', 'Clear all sockets from the plan?'))) return;
      mutate(() => { state.sockets = []; });
      toast(tr('تم مسح جميع الأفياش', 'All sockets cleared'));
      renderPanel();
    };
  }
}

window.closeDrawers = closeDrawers;
window.drawer = drawer;
