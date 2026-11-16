// 2D & Shared Application State, History (Undo/Redo), and Persistence
import { STORE, norm } from '../config.js';
import { ROOMS, WALLS } from '../data/floorplan.js';
import { defaultFurniture } from '../data/default-furniture.js';
import { autoGenerateSockets } from '../data/electrical.js';

export function defaultState() {
  const rooms = {};
  ROOMS.forEach(r => (rooms[r.id] = { name: r.name, mat: r.mat, wallMat: r.wallMat || 'alabaster' }));
  const furniture = defaultFurniture();
  const sockets = autoGenerateSockets(furniture, ROOMS, WALLS);
  return {
    furniture,
    rooms,
    demolished: [],
    measures: [],
    sockets
  };
}

export function load() {
  try {
    const s = JSON.parse(localStorage.getItem(STORE));
    if (s && Array.isArray(s.furniture)) return fixState(s);
  } catch (e) {}
  return null;
}

export function fixState(s) {
  const d = defaultState();
  s.rooms = Object.assign(d.rooms, s.rooms || {});
  ROOMS.forEach(r => {
    if (s.rooms[r.id] && !s.rooms[r.id].wallMat) {
      s.rooms[r.id].wallMat = r.wallMat || 'alabaster';
    }
  });
  s.demolished = s.demolished || [];
  s.measures = s.measures || [];
  if (!s.sockets || !Array.isArray(s.sockets) || s.sockets.length === 0) {
    s.sockets = autoGenerateSockets(s.furniture, ROOMS, WALLS);
  }
  return s;
}

export const state = load() || defaultState();
window.state = state;

export const ui = {
  tool: 'select',
  viewMode: 'plan', // 'plan' | 'elec'
  sel: null,
  mA: null,
  mCur: null,
  layers: { dims: true, labels: true, furn: true, grid: false, bearing: false, wallSnap: true, sockets: true }
};
window.ui = ui;

export const view = { x0: 0, y0: 0, s: 0.06 };
export const undoStack = [];
export const redoStack = [];
if (typeof window !== 'undefined') {
  window.undoStack = undoStack;
  window.redoStack = redoStack;
}

export function save() {
  try {
    localStorage.setItem(STORE, JSON.stringify(state));
  } catch (e) {}
}

export const snap = () => JSON.stringify(state);

let syncCallbacks = [];
export function onStateChange(cb) {
  syncCallbacks.push(cb);
}

export function notifyChange() {
  save();
  syncCallbacks.forEach(cb => cb());
  if (typeof window !== 'undefined' && typeof window.renderAll === 'function') {
    window.renderAll();
  }
}

export function commit(before) {
  const after = snap();
  if (before === after) return;
  undoStack.push(before);
  if (undoStack.length > 150) undoStack.shift();
  redoStack.length = 0;
  notifyChange();
}

export function mutate(fn) {
  const b = snap();
  fn();
  commit(b);
  if (typeof window !== 'undefined' && typeof window.renderAll === 'function') {
    window.renderAll();
  }
}

export function undo() {
  if (!undoStack.length) return false;
  redoStack.push(snap());
  const b = JSON.parse(undoStack.pop());
  Object.assign(state, b);
  validateSel();
  notifyChange();
  return true;
}

export function redo() {
  if (!redoStack.length) return false;
  undoStack.push(snap());
  const b = JSON.parse(redoStack.pop());
  Object.assign(state, b);
  validateSel();
  notifyChange();
  return true;
}

export function validateSel() {
  if (ui.sel?.kind === 'furn' && !getF(ui.sel.id)) ui.sel = null;
  if (ui.sel?.kind === 'room' && !ROOMS.some(r => r.id === ui.sel.id)) ui.sel = null;
}

export function getF(id) {
  return state.furniture.find(f => f.id === id);
}

export function aabb(f) {
  const rad = (norm(f.rot || 0) * Math.PI) / 180;
  const c = Math.abs(Math.cos(rad)), s = Math.abs(Math.sin(rad));
  const hw = (f.w * c + f.d * s) / 2, hd = (f.w * s + f.d * c) / 2;
  const arr = [f.cx - hw, f.cy - hd, f.cx + hw, f.cy + hd];
  arr.hw = hw;
  arr.hh = hd;
  return arr;
}
