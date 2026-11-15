// 3D Architectural Scene Construction (Floors, Walls, Windows, Doors, Stairs, Elevator)
import * as THREE from 'three';
import { BOUNDS, WALLS, WINS, DOORS, SLIDES, ROOMS } from '../data/floorplan.js';
import { floorMat } from './textures.js';
import { WALL_PAINTS } from '../data/materials.js';
import { wx, wz, M, H, box, cyl, mat, metal, shapeOf } from './primitives.js';

export const doors = [];
export let colliders = [];

export const clearGroup = g => {
  if (!g) return;
  g.traverse(o => {
    if (o.geometry) o.geometry.dispose();
  });
  g.clear();
};

/* ============================================================
 * Architectural PBR Materials
 * ============================================================ */
export const wallMat = mat('#f6f4ee', { roughness: 0.92 });
export const capMat = mat('#080808', { roughness: 0.98 });          // Jet black CAD cut-plane cap matching reference
export const frameMat = mat('#1c1f24', { roughness: 0.35, metalness: 0.55 }); // Obsidian black aluminum
export const sillMat = mat('#e2ded6', { roughness: 0.28 });          // Polished stone window sill ledge
export const skirtMat = mat('#3c342c', { roughness: 0.55 });         // Architectural baseboard plinth
export const edgeMat = new THREE.LineBasicMaterial({ color: 0x6f675b });
export const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0xd4ecf7,
  roughness: 0.04,
  transmission: 0.92,
  opacity: 0.35,
  transparent: true,
  depthWrite: false,
  side: THREE.DoubleSide
});

const paintMatCache = {};
export function getWallPaintMat(key) {
  if (!paintMatCache[key]) {
    const p = WALL_PAINTS[key] || WALL_PAINTS.alabaster;
    paintMatCache[key] = mat(p.sw, { roughness: p.roughness || 0.88 });
  }
  return paintMatCache[key];
}

function pointInPoly(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  return inside;
}

function roomAtPoint(x, y) {
  for (let i = 0; i < ROOMS.length; i++) {
    if (pointInPoly(x, y, ROOMS[i].poly)) return ROOMS[i].id;
  }
  return null;
}

const wallRoomCache = new Map();
function getWallRooms(rect) {
  const key = `${rect[0]},${rect[1]},${rect[2]},${rect[3]}`;
  if (!wallRoomCache.has(key)) {
    const [x0, y0, x1, y1] = rect;
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    wallRoomCache.set(key, {
      east: roomAtPoint(x1 + 60, cy),
      west: roomAtPoint(x0 - 60, cy),
      south: roomAtPoint(cx, y1 + 60),
      north: roomAtPoint(cx, y0 - 60)
    });
  }
  return wallRoomCache.get(key);
}

export function getWallMaterials(rect, state) {
  const r = getWallRooms(rect);
  const mEast = r.east ? getWallPaintMat(state?.rooms?.[r.east]?.wallMat || 'alabaster') : wallMat;
  const mWest = r.west ? getWallPaintMat(state?.rooms?.[r.west]?.wallMat || 'alabaster') : wallMat;
  const mSouth = r.south ? getWallPaintMat(state?.rooms?.[r.south]?.wallMat || 'alabaster') : wallMat;
  const mNorth = r.north ? getWallPaintMat(state?.rooms?.[r.north]?.wallMat || 'alabaster') : wallMat;
  return [mEast, mWest, capMat, wallMat, mSouth, mNorth];
}

/**
 * Builds a wall cuboid with black architectural cap on the top (+Y) face
 */
export function wallBox(rect, yb, yt, group, opt, customMat) {
  if (yt - yb <= 0.001) return null;
  const [x0, y0, x1, y1] = rect;
  const w = M(x1 - x0), h = yt - yb, d = M(y1 - y0);
  const cx = wx((x0 + x1) / 2), cy = (yb + yt) / 2, cz = wz((y0 + y1) / 2);

  // Six-sided material array: [+X, -X, +Y (top cap), -Y (bottom), +Z, -Z]
  const m = customMat || [wallMat, wallMat, capMat, wallMat, wallMat, wallMat];
  const o = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  o.position.set(cx, cy, cz);
  o.castShadow = true;
  o.receiveShadow = true;
  if (group) group.add(o);

  // Walk mode auxiliary edges & baseboard
  if (opt?.mode === 'walk') {
    const ln = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry), edgeMat);
    ln.position.copy(o.position);
    ln.userData.walkOnly = true;
    if (group) group.add(ln);

    if (yb <= 0.001) {
      const sh = Math.min(0.08, yt);
      const sk = new THREE.Mesh(new THREE.BoxGeometry(w + 0.015, sh, d + 0.015), skirtMat);
      sk.position.set(cx, sh / 2, cz);
      sk.userData.walkOnly = true;
      if (group) group.add(sk);
    }
  }

  return o;
}

/**
 * Master Architectural 3D Builder
 */
export function buildArch(ctx) {
  const { archFloor, archUp, lampG, opt, state, renderer } = ctx;
  if (!archFloor || !archUp) return;

  clearGroup(archFloor);
  clearGroup(archUp);
  if (lampG) lampG.clear();
  doors.length = 0;
  colliders = [];

  const top = opt?.cut || 2.8;

  // -------------------------------------------------------------
  // 1. FLOORS & CEILINGS
  // -------------------------------------------------------------
  ROOMS.forEach(r => {
    const matKey = state.rooms?.[r.id]?.mat || r.mat || 'wood';
    const m = floorMat(matKey, renderer);
    const isBay = r.counted === false;

    // Floor Mesh with true UV repeat
    const shape = shapeOf(r.poly);
    let fl;
    if (isBay) {
      const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.45, bevelEnabled: false });
      geo.rotateX(-Math.PI / 2);
      fl = new THREE.Mesh(geo, [m, mat('#ded8ce')]);
      fl.position.y = 0;
      fl.castShadow = true;
      fl.receiveShadow = true;
      fl.userData.room = r.id;
      archUp.add(fl);
    } else {
      const geo = new THREE.ShapeGeometry(shape);
      geo.rotateX(-Math.PI / 2);
      fl = new THREE.Mesh(geo, m);
      fl.position.y = 0;
      fl.receiveShadow = true;
      fl.userData.room = r.id;
      archFloor.add(fl);
    }

    // Ceiling (visible only when looking up indoors in Full Walls mode)
    const cg = new THREE.ShapeGeometry(shapeOf(r.poly, true));
    cg.rotateX(Math.PI / 2);
    const ceil = new THREE.Mesh(cg, mat('#fbfaf7', { roughness: 1 }));
    ceil.position.y = H;
    ceil.visible = top >= H;
    archUp.add(ceil);

    // Ceiling recessed downlight and warm interior night illumination
    if (r.at && lampG) {
      const lamp = new THREE.Mesh(
        new THREE.CylinderGeometry(0.20, 0.20, 0.02, 24),
        new THREE.MeshStandardMaterial({
          color: '#ffffff',
          emissive: '#ffe3be',
          emissiveIntensity: opt?.night ? 4.5 : 0.35
        })
      );
      lamp.position.set(wx(r.at[0]), H - 0.012, wz(r.at[1]));
      lamp.visible = top >= H;
      lampG.add(lamp);

      // Place light INSIDE room cavity below cut wall height (e.g. 1.85m)
      // so it illuminates the inner walls and floor with warm gradient falloff matching reference
      const lightY = Math.max(1.1, Math.min(top - 0.35, 1.95));
      const roomA = Math.abs(r.poly.reduce((a, [x, y], i, arr) => {
        const [nx, ny] = arr[(i + 1) % arr.length];
        return a + (x * ny - nx * y);
      }, 0) / 2) / 1000000;
      const dist = Math.max(8.5, Math.min(16.0, Math.sqrt(roomA) * 2.8));

      const pl = new THREE.PointLight(0xffdfba, opt?.night ? 18 : 0, dist, 1.45);
      pl.position.set(wx(r.at[0]), lightY, wz(r.at[1]));
      pl.userData = { nightIntensity: 18 };
      lampG.add(pl);

      // Large reception salon: add second auxiliary light to ensure uniform illumination across dining/foyer
      if (r.id === 'rec_l' || r.id === 'rec_r') {
        const auxX = r.id === 'rec_l' ? 6200 : 9600;
        const auxY = 20800;
        const pl2 = new THREE.PointLight(0xffdfba, opt?.night ? 16 : 0, dist, 1.45);
        pl2.position.set(wx(auxX), lightY, wz(auxY));
        pl2.userData = { nightIntensity: 16 };
        lampG.add(pl2);
      }
    }
  });

  // Threshold transition floor saddles
  [...DOORS, ...SLIDES].forEach(d => {
    const [x0, y0, x1, y1] = d.rect;
    const s = box(M(x1 - x0), 0.012, M(y1 - y0), mat('#d8d1c4', { roughness: 0.3 }), wx((x0 + x1) / 2), 0, wz((y0 + y1) / 2));
    s.castShadow = false;
    archFloor.add(s);
  });

  // -------------------------------------------------------------
  // 2. WALLS & BALUSTRADES
  // -------------------------------------------------------------
  WALLS.forEach((w, i) => {
    if (state.demolished?.includes('w' + i)) return;

    if (w[4] === 'low') {
      // Outdoor Terrace Balustrade: 0.25m low curb + 0.80m structural glass + metal handrail
      const curbH = Math.min(0.25, top);
      wallBox(w, 0, curbH, archUp, opt);

      if (top > 0.25) {
        const railTop = Math.min(1.05, top);
        const [x0, y0, x1, y1] = w;
        const hz = (x1 - x0) >= (y1 - y0);
        const L = M(hz ? x1 - x0 : y1 - y0);
        const cx = wx((x0 + x1) / 2);
        const cz = wz((y0 + y1) / 2);

        // Frameless structural glass balustrade
        const bGlass = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : 0.015, railTop - 0.25, hz ? 0.015 : L), glassMat);
        bGlass.position.set(cx, 0.25 + (railTop - 0.25) / 2, cz);
        archUp.add(bGlass);

        // Sleek black architectural top handrail
        const hRail = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : 0.055, 0.045, hz ? 0.055 : L), frameMat);
        hRail.position.set(cx, railTop, cz);
        hRail.castShadow = true;
        archUp.add(hRail);

        // Vertical stainless steel / bronze stanchions
        const pn = Math.max(1, Math.round(L / 1.25));
        for (let p = 0; p <= pn; p++) {
          const pt = -L / 2 + p * L / pn;
          const post = new THREE.Mesh(new THREE.BoxGeometry(hz ? 0.04 : 0.05, railTop - 0.25, hz ? 0.05 : 0.04), frameMat);
          post.position.set(cx + (hz ? pt : 0), 0.25 + (railTop - 0.25) / 2, cz + (hz ? 0 : pt));
          archUp.add(post);
        }
      }
    } else {
      // Solid wall with crisp black top cap and room-specific interior paint
      const customMats = getWallMaterials(w, state);
      wallBox(w, 0, top, archUp, opt, customMats);
    }

    colliders.push([wx(w[0]), wz(w[1]), wx(w[2]), wz(w[3])]);
  });

  // Wall lintels above door openings (only visible when top > lintel height)
  [...DOORS.map(d => [d.rect, 2.1]), ...SLIDES.map(s => [s.rect, s.v ? 2.4 : 2.1])]
    .forEach(([r, h]) => {
      if (top > h) {
        const lintelMats = getWallMaterials(r, state);
        wallBox(r, h, top, archUp, opt, lintelMats);
      }
    });

  // -------------------------------------------------------------
  // 3. ARCHITECTURAL WINDOWS (Black Aluminum Casements & Sills)
  // -------------------------------------------------------------
  WINS.forEach(r => {
    const sill = r[4] !== undefined ? r[4] : 0.9;
    const head = r[5] !== undefined ? r[5] : 2.4;

    // Solid wall below sill with room-specific interior paint
    const winWallMats = getWallMaterials(r, state);
    wallBox(r, 0, Math.min(sill, top), archUp, opt, winWallMats);

    // Solid wall above head (full walls mode)
    if (top > head) wallBox(r, head, top, archUp, opt);
    colliders.push([wx(r[0]), wz(r[1]), wx(r[2]), wz(r[3])]);

    // Effective window height in current view mode
    const gTop = Math.min(head, top);
    const [x0, y0, x1, y1] = r;
    const hz = (x1 - x0) >= (y1 - y0);
    const L = M(hz ? x1 - x0 : y1 - y0);
    const cx = wx((x0 + x1) / 2);
    const cz = wz((y0 + y1) / 2);

    // Deep architectural stone window sill ledge (extends 35mm wider than opening)
    if (top >= sill) {
      const sillMesh = new THREE.Mesh(
        new THREE.BoxGeometry(hz ? L + 0.06 : 0.32, 0.04, hz ? 0.32 : L + 0.06),
        sillMat
      );
      sillMesh.position.set(cx, sill + 0.02, cz);
      sillMesh.castShadow = true;
      sillMesh.receiveShadow = true;
      archUp.add(sillMesh);
    }

    if (gTop <= sill + 0.05) return;
    const gh = gTop - sill;

    // High-transmission architectural glass pane
    const pane = new THREE.Mesh(
      new THREE.BoxGeometry(hz ? L : 0.015, gh, hz ? 0.015 : L),
      glassMat
    );
    pane.position.set(cx, sill + gh / 2, cz);
    archUp.add(pane);

    // Obsidian black aluminum vertical mullions
    const n = Math.max(1, Math.round(L / 0.85));
    for (let k = 0; k <= n; k++) {
      const t = -L / 2 + (k * L) / n;
      const mu = new THREE.Mesh(
        new THREE.BoxGeometry(hz ? 0.045 : 0.075, gh, hz ? 0.075 : 0.045),
        frameMat
      );
      mu.position.set(cx + (hz ? t : 0), sill + gh / 2, cz + (hz ? 0 : t));
      mu.castShadow = true;
      archUp.add(mu);
    }

    // Horizontal window rails (sill rail & top cut/head rail)
    [sill + 0.025, gTop - 0.025].forEach(y => {
      const tr = new THREE.Mesh(
        new THREE.BoxGeometry(hz ? L : 0.075, 0.045, hz ? 0.075 : L),
        frameMat
      );
      tr.position.set(cx, y, cz);
      tr.castShadow = true;
      archUp.add(tr);
    });
  });

  // -------------------------------------------------------------
  // 4. LUXURY MILLWORK DOORS (Architraves, Walnut/Oak Leafs & Handles)
  // -------------------------------------------------------------
  DOORS.forEach(d => {
    const [x0, y0, x1, y1] = d.rect;
    const isHz = (d.c[0] !== 0);
    const wOpen = isHz ? (x1 - x0) : (y1 - y0);
    const wThick = isHz ? (y1 - y0) : (x1 - x0);
    const xMid = (x0 + x1) / 2, yMid = (y0 + y1) / 2;
    const hx = isHz ? (d.c[0] > 0 ? x0 : x1) : xMid;
    const hy = isHz ? yMid : (d.c[1] > 0 ? y0 : y1);

    const L = M(wOpen);
    const frameDepth = M(wThick) + 0.02;
    const dh = Math.min(2.05, top);
    const cAng = Math.atan2(-d.c[1], d.c[0]);

    // 3-Piece Millwork Architrave / Casing (wrapping wall opening centered in wall thickness)
    const frameCol = d.entry ? '#24170e' : '#423124';
    const frameM = mat(frameCol, { roughness: 0.42 });
    const fG = new THREE.Group();
    fG.position.set(wx(hx), 0, wz(hy));
    fG.rotation.y = cAng;

    // Left and right jambs
    fG.add(box(0.045, Math.min(2.12, top), frameDepth, frameM, 0.0225, 0, 0));
    fG.add(box(0.045, Math.min(2.12, top), frameDepth, frameM, L - 0.0225, 0, 0));
    // Head casing
    if (top > 2.05) {
      fG.add(box(L, 0.065, frameDepth, frameM, L / 2, Math.min(2.05, top), 0));
    }
    archUp.add(fG);

    // Pivotable Door Leaf Group
    const pivot = new THREE.Group();
    pivot.position.set(wx(hx), 0, wz(hy));

    const leaf = new THREE.Group();
    const doorWood = mat(d.entry ? '#2e1f14' : '#8a6545', { roughness: 0.38 });
    const leafW = L - 0.045;

    // Wood slab centered at leafW / 2
    const woodMesh = box(leafW, dh, 0.04, doorWood, leafW / 2, 0, 0);
    leaf.add(woodMesh);

    if (d.entry) {
      // Luxury Walnut Security Entrance Door: horizontal metal inlays & vertical ladder pull
      for (let k = 0; k < 4; k++) {
        const yPos = 0.35 + k * 0.40;
        const bar = box(leafW * 0.75, 0.012, 0.044, mat('#141414', { roughness: 0.2, metalness: 0.8 }), leafW / 2, yPos, 0);
        leaf.add(bar);
      }
      // 650mm vertical brushed stainless steel ladder pull bar
      const handleX = leafW - 0.07;
      const handleBar = cyl(0.013, 0.013, 0.65, metal('#e2e8f0'), handleX, 0.70, 0.038);
      const post1 = box(0.018, 0.018, 0.035, metal(), handleX, 0.75, 0.02);
      const post2 = box(0.018, 0.018, 0.035, metal(), handleX, 1.25, 0.02);
      leaf.add(handleBar, post1, post2);
    } else {
      // Natural French Oak Interior Door: subtle panel reliefs & ergonomic lever handle
      for (let k = 0; k < 3; k++) {
        const yPos = 0.40 + k * 0.48;
        const groove = box(leafW * 0.78, 0.01, 0.042, mat('#5a4029', { roughness: 0.48 }), leafW / 2, yPos, 0);
        leaf.add(groove);
      }
      const handleX = leafW - 0.06;
      const escPlate = box(0.04, 0.14, 0.046, metal(), handleX, 0.90, 0);
      const lever = box(0.11, 0.018, 0.018, metal(), handleX + 0.03, 0.96, 0.032);
      leaf.add(escPlate, lever);
    }

    pivot.add(leaf);

    // Interactive Hinge Setup
    const ang = v => Math.atan2(-v[1], v[0]);
    const door = { pivot, a0: ang(d.c), a1: ang(d.o), open: true };
    if (door.a1 - door.a0 > Math.PI) door.a1 -= Math.PI * 2;
    if (door.a0 - door.a1 > Math.PI) door.a1 += Math.PI * 2;
    door.cur = door.a1;
    pivot.rotation.y = door.cur;
    
    // Tag all door parts for raycasting
    pivot.userData.door = door;
    leaf.userData.door = door;
    woodMesh.userData.door = door;

    doors.push(door);
    archUp.add(pivot);
  });

  // -------------------------------------------------------------
  // 5. SLIDING GLASS PATIO DOORS (Terrace / Balcony Access)
  // -------------------------------------------------------------
  SLIDES.forEach(({ rect: [x0, y0, x1, y1], v }) => {
    const L = M(v ? y1 - y0 : x1 - x0);
    const ph = Math.min(v ? 2.4 : 2.1, top);
    const pl = L * 0.55;

    [[-1, -0.02], [1, 0.02]].forEach(([s, off]) => {
      const c = s < 0 ? -L / 2 + pl / 2 : L / 2 - pl / 2;
      const x = v ? wx((x0 + x1) / 2) + off : wx(x0) + L / 2 + c;
      const z = v ? wz(y0) + L / 2 + c : wz((y0 + y1) / 2) + off;

      // Sliding glass panel
      const p = new THREE.Mesh(new THREE.BoxGeometry(v ? 0.02 : pl, ph, v ? pl : 0.02), glassMat);
      p.position.set(x, ph / 2, z);
      archUp.add(p);

      // Top and bottom guide rails
      [ph - 0.03, 0.03].forEach(y => {
        const fr = new THREE.Mesh(new THREE.BoxGeometry(v ? 0.045 : pl, 0.05, v ? pl : 0.045), frameMat);
        fr.position.set(x, y, z);
        fr.castShadow = true;
        archUp.add(fr);
      });

      // Vertical stile frame posts & grab handles
      [-1, 1].forEach(e => {
        const fr = new THREE.Mesh(new THREE.BoxGeometry(0.045, ph, 0.045), frameMat);
        fr.position.set(v ? x : x + (e * pl) / 2, ph / 2, v ? z + (e * pl) / 2 : z);
        fr.castShadow = true;
        archUp.add(fr);
      });
    });
  });

  // -------------------------------------------------------------
  // 6. CENTRAL STAIRCASE & PANORAMIC GLASS ELEVATOR CORE
  // -------------------------------------------------------------
  buildStairsAndElevator(archUp, top);
}

/**
 * Procedural U-Shaped Staircase and Panoramic Glass Elevator
 */
function buildStairsAndElevator(group, top) {
  const stairM = mat('#faf7f2', { roughness: 0.18 });         // Calacatta marble risers
  const treadM = mat('#c29b68', { roughness: 0.35 });         // French oak treads
  const steelM = mat('#1e242b', { roughness: 0.3, metalness: 0.8 }); // Black structural steel

  // Flight 1: Climb South to North (9 steps)
  const stepH = 0.165, stepD = 0.28, stepW = 1.10;
  for (let i = 0; i < 9; i++) {
    const y = i * stepH;
    if (y + stepH > top) break;
    const z = wz(17180 - i * 314);
    const x = wx(6590);

    // Marble riser
    group.add(box(stepW, stepH, 0.04, stairM, x, y, z - stepD / 2));
    // Oak tread with bullnose nosing
    group.add(box(stepW + 0.04, 0.035, stepD + 0.03, treadM, x, y + stepH - 0.035, z));
  }

  // Mid Landing at ~1.48m
  if (top > 1.35) {
    const landY = Math.min(1.48, top);
    group.add(box(M(3720), 0.18, M(900), stairM, wx(7900), landY - 0.18, wz(13900)));
    group.add(box(M(3720), 0.035, M(900), treadM, wx(7900), landY - 0.035, wz(13900)));
  }

  // Flight 2: Climb North to South from Landing (9 steps)
  for (let i = 0; i < 9; i++) {
    const y = 1.48 + i * stepH;
    if (y + stepH > top) break;
    const z = wz(14350 + i * 314);
    const x = wx(9210);

    group.add(box(stepW, stepH, 0.04, stairM, x, y, z - stepD / 2));
    group.add(box(stepW + 0.04, 0.035, stepD + 0.03, treadM, x, y + stepH - 0.035, z));
  }

  // Stainless steel stair handrail
  const railH = Math.min(2.4, top);
  const hr1 = cyl(0.018, 0.018, 3.0, metal('#e2e8f0'), wx(6040 + 0.05), railH / 2, wz(15765));
  hr1.rotation.x = 0.52;
  group.add(hr1);

  // Panoramic Glass Elevator Enclosure
  const elW = M(1520), elD = M(2150), elH = Math.min(2.8, top);
  const elCx = wx(7900), elCz = wz(15425);

  // Four structural steel corner columns
  [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => {
    group.add(box(0.065, elH, 0.065, steelM, elCx + (sx * elW) / 2, 0, elCz + (sz * elD) / 2));
  });

  // Four panoramic glass enclosure walls
  group.add(box(elW, elH, 0.015, glassMat, elCx, 0, elCz - elD / 2));
  group.add(box(elW, elH, 0.015, glassMat, elCx, 0, elCz + elD / 2));
  group.add(box(0.015, elH, elD, glassMat, elCx - elW / 2, 0, elCz));
  group.add(box(0.015, elH, elD, glassMat, elCx + elW / 2, 0, elCz));

  // Illuminated Elevator Cabin inside
  const cabH = Math.min(2.2, top);
  group.add(box(elW - 0.16, 0.05, elD - 0.16, steelM, elCx, 0.02, elCz)); // Stainless steel floor
  if (top > 1.2) {
    // Stainless steel handrail inside cabin
    const cRail = new THREE.Mesh(new THREE.BoxGeometry(elW - 0.22, 0.035, 0.035), metal('#e2e8f0'));
    cRail.position.set(elCx, 0.95, elCz - elD / 2 + 0.08);
    group.add(cRail);
  }
}
