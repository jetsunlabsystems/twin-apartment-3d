// 3D Three.js Main Scene, Lighting, Camera Controllers & Render Loop
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

import { $, COARSE, TAP, esc, fmt, area } from '../config.js';
import { tr, nm, LANG } from '../i18n.js';
import { BOUNDS, ROOMS } from '../data/floorplan.js';
import { state, ui, view, commit, snap, getF } from '../2d/state.js';
import { select, snapMove } from '../2d/interactions.js';
import { drawer } from '../ui/panels.js';
import { renderAll } from '../2d/renderer.js';
import { OX, OY, wx, wz, M, H, box, cyl, mat, metal } from './primitives.js';
import { buildFurniture } from './furniture-models.js';
import { buildArch, doors, colliders, clearGroup, glassMat, wallMat, capMat, frameMat } from './arch-builder.js';

const stage = $('#stage'), host = $('#view3d');
const FOV = 58;
const SW = () => stage?.clientWidth || window.innerWidth;
const SH = () => stage?.clientHeight || window.innerHeight;

export const opt = { cut: 2.8, furn: true, labels: true, night: false, hour: 10, mode: 'orbit' };

let inited = false, active = false, raf = 0, anim = null, fly = null;
let renderer, labelRenderer, scene, camera, orbit, walkCtl, hemi, sun, ground;
let archFloor, archUp, furnG, labelG, lampG, selKey = null, selHelper = null;
let sigArch = '', sigFurn = '', sigLabels = '', grow = 1, furnGrow = 1;
const keys = {};

/* ======================= Initialization ======================= */
export function init3D() {
  if (inited) return;
  inited = true;

  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(SW(), SH());
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  host.prepend(renderer.domElement);

  labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(SW(), SH());
  Object.assign(labelRenderer.domElement.style, { position: 'absolute', inset: '0', pointerEvents: 'none' });
  host.appendChild(labelRenderer.domElement);

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(FOV, SW() / SH(), 0.05, 400);

  orbit = new OrbitControls(camera, renderer.domElement);
  orbit.enableDamping = true;
  orbit.maxPolarAngle = Math.PI * 0.495;
  orbit.minDistance = 2.0;
  orbit.maxDistance = 120;

  walkCtl = new PointerLockControls(camera, document.body);
  walkCtl.addEventListener('lock', () => {
    $('#walkOverlay').style.display = 'none';
    $('#cross').style.display = 'block';
  });
  walkCtl.addEventListener('unlock', () => {
    if (opt.mode === 'walk') {
      $('#walkOverlay').style.display = 'flex';
      $('#cross').style.display = 'none';
    }
  });

  hemi = new THREE.HemisphereLight(0xfff8ee, 0xb9a88f, 1.15);
  sun = new THREE.DirectionalLight(0xfff1dd, 2.8);
  sun.castShadow = true;
  sun.shadow.mapSize.setScalar(COARSE ? 2048 : 4096);

  // Directional shadow camera bounds covering the entire 17.8m x 27.7m twin apartment
  Object.assign(sun.shadow.camera, {
    left: -18,
    right: 18,
    top: 20,
    bottom: -20,
    near: 1,
    far: 80
  });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;

  // Generous architectural ground plane
  ground = new THREE.Mesh(
    new THREE.PlaneGeometry(280, 280),
    new THREE.MeshStandardMaterial({ color: 0xf2eee7, roughness: 1 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.015;
  ground.receiveShadow = true;
  scene.add(hemi, sun, sun.target, ground);

  // Environment reflections
  const pm = new THREE.PMREMGenerator(renderer);
  const envTex = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environment = envTex;
  pm.dispose();

  archFloor = new THREE.Group();
  archUp = new THREE.Group();
  furnG = new THREE.Group();
  labelG = new THREE.Group();
  lampG = new THREE.Group();
  scene.add(archFloor, archUp, furnG, labelG, lampG);

  const cv = renderer.domElement;
  let downAt = null, look = null;

  cv.addEventListener('pointerdown', e => {
    downAt = [e.clientX, e.clientY];
    if (typeof window.closeDrawers === 'function') window.closeDrawers();
    if (touchWalk && !look) {
      look = { id: e.pointerId, x: e.clientX, y: e.clientY };
      try { cv.setPointerCapture(e.pointerId); } catch(err) {}
    }
  });

  cv.addEventListener('pointermove', e => {
    if (!look || e.pointerId !== look.id) return;
    lookBy(e.clientX - look.x, e.clientY - look.y);
    look.x = e.clientX;
    look.y = e.clientY;
  });

  cv.addEventListener('pointercancel', e => {
    if (look?.id === e.pointerId) look = null;
  });

  // Furniture 3D Drag & Drop (snaps with 2D walls & grid)
  let fdrag = null;
  host.addEventListener('pointerdown', e => {
    if (e.target !== cv || !e.isPrimary || anim || opt.mode !== 'orbit' || ui.sel?.kind !== 'furn') return;
    const h = pick(e);
    const f = h?.fid === ui.sel.id && getF(h.fid);
    const g = f && groundAt(e.clientX, e.clientY);
    if (!g) return;
    fdrag = { id: f.id, pid: e.pointerId, sx: e.clientX, sy: e.clientY, ox: g.x - f.cx, oy: g.y - f.cy, before: snap(), moved: false };
    orbit.enabled = false;
    fly = null;
    try { cv.setPointerCapture(e.pointerId); } catch(err) {}
  }, true);

  cv.addEventListener('pointermove', e => {
    if (!fdrag || e.pointerId !== fdrag.pid) return;
    if (!fdrag.moved && Math.hypot(e.clientX - fdrag.sx, e.clientY - fdrag.sy) < TAP) return;
    const f = getF(fdrag.id);
    const g = groundAt(e.clientX, e.clientY);
    if (!f || !g) return;
    fdrag.moved = true;
    cv.style.cursor = 'grabbing';
    [f.cx, f.cy] = snapMove(f, g.x - fdrag.ox, g.y - fdrag.oy);
    furnG.children.find(o => o.userData.fid === f.id)?.position.set(wx(f.cx), 0, wz(f.cy));
  });

  const endF = e => {
    if (!fdrag || e.pointerId !== fdrag.pid) return;
    const d = fdrag;
    fdrag = null;
    orbit.enabled = true;
    cv.style.cursor = '';
    if (d.moved) {
      commit(d.before);
      renderAll();
    }
  };
  cv.addEventListener('pointerup', endF);
  cv.addEventListener('pointercancel', endF);

  // Interactive Clicks: Doors Open/Close & Furniture/Room Selection
  cv.addEventListener('pointerup', e => {
    const tap = downAt && Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) <= TAP;
    if (look?.id === e.pointerId) {
      look = null;
      if (tap) {
        const h = pick(e);
        if (h?.door && h.dist < 3.5) h.door.open = !h.door.open;
      }
      return;
    }
    if (anim || opt.mode !== 'orbit' || !tap) return;
    const h = pick(e);
    if (h?.door) {
      h.door.open = !h.door.open;
    } else if (h?.fid) {
      select({ kind: 'furn', id: h.fid });
      drawer('panel', true);
    } else if (h?.room) {
      select({ kind: 'room', id: h.room });
      drawer('panel', true);
    } else {
      select(null);
    }
  });

  new ResizeObserver(() => {
    renderer.setSize(SW(), SH());
    labelRenderer.setSize(SW(), SH());
    camera.aspect = SW() / SH();
    camera.updateProjectionMatrix();
  }).observe(stage);

  bindUI();
}

/* ======================= Scene Synchronization & Construction ======================= */
export function buildFurn() {
  clearGroup(furnG);
  state.furniture.forEach(f => furnG.add(buildFurniture(f)));
  furnG.visible = opt.furn;
  selKey = null;
  applyGrow();
}

export function buildLabels() {
  labelG.children.slice().forEach(o => {
    if (o.element) o.element.remove();
    labelG.remove(o);
  });

  ROOMS.filter(r => r.at).forEach(r => {
    const el = document.createElement('div');
    el.className = 'rlabel';
    el.innerHTML = `<span>${esc(nm(state.rooms?.[r.id]?.name || r.name))}</span><small>${area(r.poly).toFixed(1)}m²</small>`;
    el.onclick = (e) => {
      e.stopPropagation();
      select({ kind: 'room', id: r.id });
      drawer('panel', true);
      flyToRoom(r.id);
    };
    const o = new CSS2DObject(el);
    // Sit slightly above floor/furniture (y = 0.85m), floating cleanly matching reference render
    o.position.set(wx(r.at[0]), 0.85, wz(r.at[1]));
    o.visible = labelG.visible && opt.labels;
    labelG.add(o);
  });

  const counted = ROOMS.filter(r => r.counted !== false);
  const roomList = $('#roomList');
  if (roomList) {
    roomList.innerHTML = counted.map(r => `<button data-room="${r.id}"><span>${esc(nm(state.rooms?.[r.id]?.name || r.name))}</span><small>${area(r.poly).toFixed(2)} m²</small></button>`).join('')
      + `<button data-room="__all"><span>${tr('كامل الشقة', 'Whole home')}</span><small>${counted.reduce((a, r) => a + area(r.poly), 0).toFixed(2)} m²</small></button>`;
    roomList.querySelectorAll('button').forEach(b => {
      b.onclick = () => {
        roomList.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        if (opt.mode === 'walk') setMode('orbit');
        if (b.dataset.room === '__all') {
          select(null);
          flyTo(isoWhole());
        } else {
          select({ kind: 'room', id: b.dataset.room });
          drawer('panel', true);
          flyToRoom(b.dataset.room);
        }
      };
    });
  }
}

export function showLabels(v) {
  labelG.visible = !!v;
  labelG.children.forEach(o => {
    o.visible = !!v;
    if (o.element) o.element.style.display = v ? '' : 'none';
  });
  if (labelRenderer && scene && camera) {
    labelRenderer.render(scene, camera);
  }
}

export function applyGrow() {
  if (!inited) return;
  if (archUp) archUp.scale.y = Math.max(grow, 0.001);
  if (furnG) furnG.scale.y = Math.max(furnGrow, 0.001);
  if (lampG) lampG.visible = grow > 0.99;
}

export function sync(force) {
  if (!inited || (!active && !force)) return;
  const a = JSON.stringify([state.rooms, state.demolished, opt.cut]);
  const f = JSON.stringify(state.furniture);
  const l = JSON.stringify([state.rooms, opt.cut]);

  if (force || a !== sigArch) {
    sigArch = a;
    buildArch({ archFloor, archUp, lampG, opt, state, renderer });
  }
  if (force || f !== sigFurn) {
    sigFurn = f;
    buildFurn();
  }
  if (force || l !== sigLabels) {
    sigLabels = l;
    buildLabels();
  }
}

/* ======================= Lighting & Daylight System ======================= */
export function applyLight() {
  const t = (opt.hour - 6) / 12;
  const az = Math.PI * (0.15 + t * 0.7);
  const el = Math.sin(Math.PI * t) * 1.05 + 0.15;
  const warm = 1 - Math.sin(Math.PI * t);

  sun.position.set(Math.cos(az) * 22, Math.sin(el) * 24 + 4, -Math.sin(az) * 14 + 10);
  sun.target.position.set(0, 0, 0);
  sun.color.setHSL(0.09, 0.5 + warm * 0.4, 0.92 - warm * 0.12);

  if (opt.night) {
    // Pure pitch-black night environment matching the reference render
    sun.intensity = 0;
    hemi.intensity = 0.04;
    hemi.color.set(0x1e293b);
    hemi.groundColor.set(0x000000);
    scene.background = new THREE.Color(0x000000);
    ground.visible = false;
  } else {
    // Crisp architectural daylight
    sun.intensity = 1.4 + Math.sin(Math.PI * t) * 1.6;
    hemi.intensity = 1.15;
    hemi.color.set(0xfff8ee);
    hemi.groundColor.set(0xb9a88f);
    scene.background = new THREE.Color(0xf7f4ee);
    ground.visible = true;
    ground.material.color.set(0xf2eee7);
  }

  lampG.children.forEach(o => {
    if (o.isPointLight) {
      o.intensity = opt.night ? (o.userData?.nightIntensity || 18) : 0;
    } else if (o.material) {
      o.material.emissiveIntensity = opt.night ? 4.5 : 0.35;
    }
  });

  renderer.toneMappingExposure = opt.night ? 1.35 : 1.05;

  const h = Math.floor(opt.hour);
  const m = Math.round((opt.hour - h) * 60);
  const sunT = $('#sunT');
  if (sunT) sunT.textContent = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

/* ======================= Camera Poses & Easing ======================= */
const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);
const clamp01 = t => Math.max(0, Math.min(1, t));
const pose = (t, p) => ({ t, p });

function planPose() {
  const cx = view.x0 + SW() / 2 / view.s;
  const cy = view.y0 + SH() / 2 / view.s;
  const visH = SH() / view.s / 1000;
  const dist = visH / 2 / Math.tan((FOV / 2) * Math.PI / 180);
  const t = new THREE.Vector3(wx(cx), 0, wz(cy));
  return pose(t, t.clone().add(new THREE.Vector3(0, dist, 1e-4)));
}

function isoFrom(t, d = 26) {
  const p = t.clone().add(new THREE.Vector3(12, 22, 16).normalize().multiplyScalar(d));
  return pose(t, p);
}

// Framing the entire 17.8m x 27.7m luxury twin apartment
const isoWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(13, 27, 21));
const topWhole = () => pose(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 36, 1e-4));
const curPose = () => pose(orbit.target.clone(), camera.position.clone());

function camTween(A, B, e) {
  const t = A.t.clone().lerp(B.t, e);
  const sa = new THREE.Spherical().setFromVector3(A.p.clone().sub(A.t));
  const sb = new THREE.Spherical().setFromVector3(B.p.clone().sub(B.t));
  let dth = sb.theta - sa.theta;
  dth = Math.atan2(Math.sin(dth), Math.cos(dth));
  const s = new THREE.Spherical(
    sa.radius + (sb.radius - sa.radius) * e,
    sa.phi + (sb.phi - sa.phi) * e,
    sa.theta + dth * e
  );
  camera.position.copy(t).add(new THREE.Vector3().setFromSpherical(s));
  camera.lookAt(t);
  orbit.target.copy(t);
}

function setPose(P) {
  camera.position.copy(P.p);
  orbit.target.copy(P.t);
  camera.lookAt(P.t);
}

function animate(dur, fn) {
  return new Promise(res => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      try { fn(1); } catch (e) {}
      if (anim && anim.res === finish) anim = null;
      res();
    };
    anim = { dur, fn, t0: performance.now(), res: finish };
    setTimeout(finish, dur + 120);
  });
}
const wait = ms => new Promise(r => setTimeout(r, ms));

function flyTo(targetPose, dur = 900) {
  if (anim) return;
  fly = { A: curPose(), B: targetPose, t0: performance.now(), dur };
}

function flyToRoom(id) {
  const r = ROOMS.find(x => x.id === id);
  if (!r) return;
  const p = r.poly;
  const xs = p.map(pt => pt[0]);
  const ys = p.map(pt => pt[1]);
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
  const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
  const maxSpan = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) / 1000;
  const d = Math.max(5.5, maxSpan * 1.55);
  flyTo(isoFrom(new THREE.Vector3(wx(cx), 0, wz(cy)), d));
}

/* ======================= 2D / 3D Mode Switching ======================= */
export async function enter() {
  if (active || anim) return;
  init3D();
  active = true;
  host.classList.add('active');
  stage.classList.add('animating');

  sync(true);
  applyLight();
  setMode('orbit');
  showLabels(false);

  grow = 0.001;
  furnGrow = 0.001;
  applyGrow();
  setPose(planPose());

  renderer.render(scene, camera);
  startLoop();

  const P0 = curPose();
  const P1 = isoWhole();

  await animate(500, t => {
    stage.classList.toggle('mid', t > 0.08);
  });
  stage.classList.remove('mid');
  stage.classList.add('in3d');

  await animate(850, t => {
    const e = ease(t);
    camTween(P0, P1, e);
    grow = e;
    furnGrow = e;
    applyGrow();
  });
  grow = 1;
  furnGrow = 1;
  applyGrow();
  setPose(P1);

  stage.classList.remove('animating');
  showLabels(opt.labels);
}

export async function exit() {
  if (!active || anim) return;
  if (opt.mode === 'walk') setMode('orbit');
  anim = true;
  stage.classList.add('animating');
  showLabels(false);

  const P0 = curPose();
  const P1 = planPose();

  animate(1050, t => camTween(P0, P1, ease(t)));
  await animate(400, t => {
    furnGrow = 1 - ease(t);
    applyGrow();
  });
  furnGrow = 0.001;
  applyGrow();

  await animate(550, t => {
    grow = 1 - ease(t);
    applyGrow();
  });
  grow = 0.001;
  applyGrow();

  stage.classList.add('mid');
  await wait(80);
  stage.classList.remove('in3d', 'mid', 'animating');
  host.classList.remove('active');
  active = false;
  anim = null;
  cancelAnimationFrame(raf);
  raf = 0;
  if (selHelper) selHelper.visible = false;
}

/* ======================= Raycasting & Object Picking ======================= */
const ray = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function pick(e) {
  if (e) {
    const cv = renderer?.domElement;
    if (cv) {
      const rect = cv.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      mouse.set(x, y);
    } else {
      mouse.set((e.clientX / SW()) * 2 - 1, -(e.clientY / SH()) * 2 + 1);
    }
  } else {
    mouse.set(0, 0);
  }
  ray.setFromCamera(mouse, camera);

  const hits = ray.intersectObjects([furnG, archFloor, archUp], true);
  for (const h of hits) {
    let p = h.object;
    while (p && p !== scene) {
      if (p.userData.door) return { door: p.userData.door, dist: h.distance };
      if (p.userData.fid) return { fid: p.userData.fid, dist: h.distance };
      if (p.userData.room) return { room: p.userData.room, dist: h.distance };
      p = p.parent;
    }
  }
  return null;
}

function groundAt(cx, cy) {
  const cv = renderer?.domElement;
  if (cv) {
    const rect = cv.getBoundingClientRect();
    const x = ((cx - rect.left) / rect.width) * 2 - 1;
    const y = -((cy - rect.top) / rect.height) * 2 + 1;
    mouse.set(x, y);
  } else {
    mouse.set((cx / SW()) * 2 - 1, -(cy / SH()) * 2 + 1);
  }
  ray.setFromCamera(mouse, camera);
  const hits = ray.intersectObject(ground);
  if (!hits.length) return null;
  const p = hits[0].point;
  return { x: p.x * 1000 + OX, y: p.z * 1000 + OY };
}

function updateSel() {
  if (!active) return;
  const f = ui.sel?.kind === 'furn' && opt.furn && getF(ui.sel.id);
  const key = f ? `${f.id}_${f.cx}_${f.cy}_${f.rot}_${f.w}_${f.d}` : null;
  if (key === selKey) return;
  selKey = key;

  if (!f) {
    if (selHelper) selHelper.visible = false;
    return;
  }
  if (!selHelper) {
    const boxGeo = new THREE.BoxGeometry(1, 1, 1);
    selHelper = new THREE.LineSegments(
      new THREE.EdgesGeometry(boxGeo),
      new THREE.LineBasicMaterial({ color: 0xb5653a, linewidth: 2 })
    );
    scene.add(selHelper);
  }

  const model = furnG.children.find(o => o.userData.fid === f.id);
  if (model) {
    const aabb = new THREE.Box3().setFromObject(model);
    const sz = aabb.getSize(new THREE.Vector3());
    const c = aabb.getCenter(new THREE.Vector3());
    selHelper.scale.copy(sz);
    selHelper.position.copy(c);
    selHelper.visible = true;
  }
}

/* ======================= First Person Walk Mode ======================= */
let touchWalk = false;

function lookBy(dx, dy) {
  const euler = new THREE.Euler(0, 0, 0, 'YXZ');
  euler.setFromQuaternion(camera.quaternion);
  euler.y -= dx * 0.0028;
  euler.x = Math.max(-Math.PI * 0.45, Math.min(Math.PI * 0.45, euler.x - dy * 0.0028));
  camera.quaternion.setFromEuler(euler);
}

function startTouchWalk() {
  touchWalk = true;
  $('#walkOverlay').style.display = 'none';
  $('#walkStick').style.display = 'block';
  $('#walkExit').style.display = 'flex';
}

function stopTouchWalk() {
  touchWalk = false;
  $('#walkStick').style.display = 'none';
  $('#walkExit').style.display = 'none';
}

let joyVec = { x: 0, y: 0 };
function bindJoystick() {
  const stick = $('#walkStick'), knob = $('#walkKnob');
  if (!stick || !knob) return;
  const R = 45;
  let pid = null, sx = 0, sy = 0;

  stick.addEventListener('pointerdown', e => {
    pid = e.pointerId;
    try { stick.setPointerCapture(pid); } catch(err) {}
    const rect = stick.getBoundingClientRect();
    sx = rect.left + rect.width / 2;
    sy = rect.top + rect.height / 2;
  });

  stick.addEventListener('pointermove', e => {
    if (e.pointerId !== pid) return;
    const dx = e.clientX - sx, dy = e.clientY - sy, d = Math.hypot(dx, dy);
    const k = d > R ? R / d : 1;
    const kx = dx * k, ky = dy * k;
    knob.style.transform = `translate(${kx}px, ${ky}px)`;
    joyVec = { x: kx / R, y: -ky / R };
  });

  const endJ = e => {
    if (e.pointerId !== pid) return;
    pid = null;
    knob.style.transform = '';
    joyVec = { x: 0, y: 0 };
  };
  stick.addEventListener('pointerup', endJ);
  stick.addEventListener('pointercancel', endJ);
}

function setMode(mode) {
  if (opt.mode === mode) return;
  opt.mode = mode;
  syncModeBtns();
  syncCutBtns();
  showLabels(opt.labels && mode === 'orbit');
  stage.classList.toggle('walking', mode === 'walk');

  if (mode === 'walk') {
    camera.fov = 68;
    camera.updateProjectionMatrix();
    orbit.enabled = false;
    const d0 = DOORS.find(d => d.entry) || DOORS[0];
    const sp = d0 ? [wx(d0.h[0]) - d0.c[0] * 0.9, wz(d0.h[1]) - d0.c[1] * 0.9] : [0, 0];
    camera.position.set(sp[0], 1.62, sp[1]);
    camera.lookAt(sp[0] + (d0 ? d0.c[0] : 0), 1.62, sp[1] + (d0 ? d0.c[1] : 1));
    $('#walkOverlay').style.display = 'flex';
  } else {
    camera.fov = FOV;
    camera.updateProjectionMatrix();
    stopTouchWalk();
    if (walkCtl.isLocked) walkCtl.unlock();
    $('#walkOverlay').style.display = 'none';
    $('#cross').style.display = 'none';
    orbit.enabled = true;
    flyTo(isoWhole(), 600);
  }
}

function blocked(x, z, r = 0.22) {
  for (const c of colliders) {
    const [x0, z0, x1, z1] = c;
    const dx = x1 - x0, dz = z1 - z0, L2 = dx * dx + dz * dz;
    const t = L2 === 0 ? 0 : Math.max(0, Math.min(1, ((x - x0) * dx + (z - z0) * dz) / L2));
    if (Math.hypot(x - (x0 + t * dx), z - (z0 + t * dz)) < r) return true;
  }
  return false;
}

function stepWalk(dt) {
  let fwd = 0, side = 0;
  if (keys.KeyW || keys.ArrowUp) fwd += 1;
  if (keys.KeyS || keys.ArrowDown) fwd -= 1;
  if (keys.KeyA || keys.ArrowLeft) side -= 1;
  if (keys.KeyD || keys.ArrowRight) side += 1;
  if (touchWalk) {
    fwd += joyVec.y;
    side += joyVec.x;
  }
  if (!fwd && !side) return;

  const spd = (keys.ShiftLeft || keys.ShiftRight ? 4.5 : 2.4) * dt;
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  dir.y = 0;
  dir.normalize();
  const right = new THREE.Vector3().crossVectors(dir, new THREE.Vector3(0, 1, 0)).normalize();

  const mv = new THREE.Vector3()
    .addScaledVector(dir, fwd)
    .addScaledVector(right, side)
    .normalize()
    .multiplyScalar(spd);
  const p = camera.position;
  if (!blocked(p.x + mv.x, p.z)) p.x += mv.x;
  if (!blocked(p.x, p.z + mv.z)) p.z += mv.z;
}

addEventListener('keydown', e => {
  if (!active || e.target.matches('input,select,textarea')) return;
  keys[e.code] = true;
  if (opt.mode === 'walk' && e.code === 'KeyE') {
    const h = pick();
    if (h?.door && h.dist < 2.5) h.door.open = !h.door.open;
  }
});
addEventListener('keyup', e => (keys[e.code] = false));

/* ======================= UI Synchronization ======================= */
function syncModeBtns() {
  document.querySelectorAll('#modes3d .btn').forEach(b => b.classList.toggle('on', b.dataset.mode === opt.mode));
}
function syncCutBtns() {
  document.querySelectorAll('[data-cut]').forEach(b => b.classList.toggle('on', +b.dataset.cut === opt.cut));
}
function syncWalkTexts() {
  const t = COARSE
    ? [tr('انقر للبدء، من باب الشقة', 'Tap to start at front door'), tr('عصا التحكم للحركة · اسحب للالتفات', 'Joystick moves · drag to look'), tr('انقر على الأبواب لفتحها', 'Tap doors to open')]
    : [tr('انقر للبدء، من باب الشقة', 'Click to start at front door'), tr('WASD للحركة · الفأرة للالتفات · Shift للجري', 'WASD move · mouse looks · Shift runs'), tr('E لفتح أو إغلاق الباب القريب', 'E opens nearby doors')];
  t.forEach((h, i) => {
    const el = $('#wo' + (i + 1));
    if (el) el.innerHTML = h;
  });
}

function bindUI() {
  document.querySelectorAll('#modes3d .btn').forEach(b => (b.onclick = () => setMode(b.dataset.mode)));
  const walkOverlay = $('#walkOverlay');
  if (walkOverlay) {
    walkOverlay.onclick = () => (COARSE ? startTouchWalk() : walkCtl.lock());
  }
  document.addEventListener('pointerlockerror', () => {
    if (active && opt.mode === 'walk') startTouchWalk();
  });
  const walkExit = $('#walkExit');
  if (walkExit) walkExit.onclick = () => setMode('orbit');
  bindJoystick();
  syncWalkTexts();

  const vIso = $('#vIso');
  if (vIso) vIso.onclick = () => { if (opt.mode === 'walk') setMode('orbit'); else flyTo(isoWhole()); };
  const vTop = $('#vTop');
  if (vTop) vTop.onclick = () => { if (opt.mode === 'walk') setMode('orbit'); else flyTo(topWhole()); };

  document.querySelectorAll('[data-cut]').forEach(b => {
    b.onclick = () => {
      if (opt.mode === 'walk') return;
      opt.cut = +b.dataset.cut;
      syncCutBtns();
      sync(true);
    };
  });

  document.querySelectorAll('#toggles3d .btn').forEach(b => {
    b.onclick = () => {
      const k = b.dataset.t;
      opt[k] = !opt[k];
      b.classList.toggle('on', opt[k]);
      if (k === 'furn') {
        furnG.visible = opt.furn;
        if (!opt.furn && ui.sel?.kind === 'furn' && typeof window.select === 'function') window.select(null);
      }
      if (k === 'labels') showLabels(opt.labels && opt.mode === 'orbit' && !anim);
      if (k === 'night') applyLight();
    };
  });

  const sunInput = $('#sun');
  if (sunInput) {
    sunInput.oninput = e => {
      opt.hour = +e.target.value;
      applyLight();
    };
  }
}

/* ======================= Main Render Loop ======================= */
const clock = new THREE.Clock();
function startLoop() {
  if (!raf) {
    clock.getDelta();
    raf = requestAnimationFrame(loop);
  }
}

function loop() {
  raf = requestAnimationFrame(loop);
  try {
    const dt = Math.min(clock.getDelta(), 0.05);
    const now = performance.now();

    if (anim) {
      const t = clamp01((now - anim.t0) / anim.dur);
      anim.fn(t);
      if (t >= 1) {
        const r = anim.res;
        anim = null;
        r();
      }
    } else if (fly) {
      const t = clamp01((now - fly.t0) / fly.dur);
      camTween(fly.A, fly.B, ease(t));
      if (t >= 1) fly = null;
    } else if (opt.mode === 'orbit') {
      orbit.update();
    } else {
      stepWalk(dt);
    }

    doors.forEach(d => {
      const tg = d.open ? d.a1 : d.a0;
      d.cur += (tg - d.cur) * Math.min(1, dt * 6);
      d.pivot.rotation.y = d.cur;
    });

    updateSel();
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  } catch (err) {
    console.error('Three.js Loop Error:', err);
  }
}

export function shot() {
  const a = document.createElement('a');
  a.download = tr('شقة_مزدوجة_فاخرة_3D', 'twin-apartment-luxury-3d') + '.png';
  a.href = renderer.domElement.toDataURL('image/png');
  a.click();
}

export function relang() {
  syncWalkTexts();
  if (inited) buildLabels();
}

export function setNight(val) {
  opt.night = (val !== undefined) ? !!val : !opt.night;
  const nightBtn = document.querySelector('button[data-t="night"]');
  if (nightBtn) nightBtn.classList.toggle('on', opt.night);
  applyLight();
  return opt.night;
}

export const View3D = {
  enter,
  exit,
  relang,
  sync: () => sync(true),
  shot,
  groundAt,
  flyToRoom: id => active && !anim && flyToRoom(id),
  walking: () => active && opt.mode === 'walk',
  opt,
  applyLight,
  setNight
};
window.View3D = View3D;
