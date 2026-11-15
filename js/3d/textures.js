// Procedural Canvas Textures for PBR Architectural Flooring
import * as THREE from 'three';
import { rng, rgbK } from '../config.js';
import { WALL_PAINTS } from '../data/materials.js';

export const TEX = {
  marble:   { sx: 1.2, sy: 1.2, base: '#fbf9f5', grout: '#ddd6c9', rough: 0.10 },
  wood:     { sx: 1.8, sy: 0.36, base: '#d6b58a', rough: 0.32 },
  walnut:   { sx: 1.8, sy: 0.36, base: '#6d4a30', rough: 0.35 },
  tile800:  { sx: 0.8, sy: 0.8, base: '#ebe5da', grout: '#cfc5b4', rough: 0.20 },
  tile600:  { sx: 0.6, sy: 0.6, base: '#4e565c', grout: '#34393e', rough: 0.28 },
  antislip: { sx: 0.3, sy: 0.3, base: '#363d43', grout: '#202529', rough: 0.75 },
  terrace:  { sx: 1.6, sy: 0.14, base: '#ad7d52', grout: '#2a1e16', rough: 0.45 },
  terrazzo: { sx: 0.6, sy: 0.6, base: '#ebe4d8', grout: '#cfc8bb', rough: 0.28 },
  carpet:   { sx: 0.3, sy: 0.3, base: '#c6bfd2', rough: 1.0 }
};

export const floorMats = {};

export function floorMat(kind, renderer) {
  if (floorMats[kind]) return floorMats[kind];
  const s = TEX[kind] || TEX.tile800;
  const R = rng(kind ? kind.length * 977 + 13 : 42);
  const cv = document.createElement('canvas');
  const isWood = kind === 'wood' || kind === 'walnut';
  const isDeck = kind === 'terrace';

  cv.width = (isWood || isDeck) ? 1024 : 1024;
  cv.height = (isWood || isDeck) ? 256 : 1024;
  const g = cv.getContext('2d');
  const W = cv.width;
  const Hh = cv.height;

  g.fillStyle = s.base;
  g.fillRect(0, 0, W, Hh);

  if (isWood) {
    // Warm French Oak Parquet Planks with Natural Grain & Staggered Joints
    const rowH = Hh / 2;
    const joints = [[W * 0.68], [W * 0.34]];
    for (let r = 0; r < 2; r++) {
      let x0 = 0;
      [...joints[r], W].forEach(x1 => {
        // Individual plank tone variation
        g.fillStyle = rgbK(s.base, 0.92 + R() * 0.16);
        g.fillRect(x0, r * rowH, x1 - x0, rowH);

        // Organic wood grain curves
        g.strokeStyle = rgbK(s.base, 0.76);
        g.globalAlpha = 0.32;
        g.lineWidth = 1.3;
        for (let k = 0; k < 9; k++) {
          const y = r * rowH + 6 + R() * (rowH - 12);
          g.beginPath();
          g.moveTo(x0, y);
          for (let x = x0; x <= x1; x += 32) {
            g.lineTo(x, y + Math.sin(x * 0.024 + k) * 3.0);
          }
          g.stroke();
        }
        g.globalAlpha = 1;

        // Beveled butt joint
        g.fillStyle = rgbK(s.base, 0.52);
        g.fillRect(x1 - 2, r * rowH, 4, rowH);
        x0 = x1;
      });

      // Beveled edge seam
      g.fillStyle = rgbK(s.base, 0.50);
      g.fillRect(0, r * rowH, W, 3.5);
    }
  } else if (isDeck) {
    // Outdoor Teak / Composite Decking Slats
    const rowH = Hh / 4;
    for (let r = 0; r < 4; r++) {
      g.fillStyle = rgbK(s.base, 0.95 + R() * 0.10);
      g.fillRect(0, r * rowH + 3, W, rowH - 6);
      g.strokeStyle = rgbK(s.base, 0.70);
      g.globalAlpha = 0.25;
      g.lineWidth = 1.0;
      for (let k = 0; k < 4; k++) {
        const y = r * rowH + 4 + R() * (rowH - 8);
        g.beginPath();
        g.moveTo(0, y);
        for (let x = 0; x <= W; x += 40) {
          g.lineTo(x, y + Math.sin(x * 0.015 + k) * 1.5);
        }
        g.stroke();
      }
      g.globalAlpha = 1;
      // Deep shadow gap between decking slats
      g.fillStyle = s.grout;
      g.fillRect(0, r * rowH, W, 4);
    }
  } else if (kind === 'marble') {
    // Italian Calacatta / Statuario Marble Slabs
    for (let c = 0; c < 16; c++) {
      const grad = g.createRadialGradient(R() * W, R() * Hh, 25, R() * W, R() * Hh, 260);
      grad.addColorStop(0, 'rgba(235,226,214,0.48)');
      grad.addColorStop(1, 'rgba(251,249,245,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, Hh);
    }

    // Branching grey and golden amber veins
    const veinColors = [
      'rgba(130,120,105,0.42)',
      'rgba(195,155,95,0.38)',
      'rgba(110,105,95,0.32)'
    ];
    for (let k = 0; k < 10; k++) {
      g.strokeStyle = veinColors[k % veinColors.length];
      g.lineWidth = 1.2 + R() * 3.6;
      g.beginPath();
      let x = R() * W, y = 0;
      g.moveTo(x, y);
      for (let sStep = 0; sStep < 4; sStep++) {
        const nx = x + (R() - 0.32) * W * 0.6;
        const ny = y + Hh * 0.25;
        g.bezierCurveTo(x + (R() - 0.5) * 120, y + 60, nx + (R() - 0.5) * 120, ny - 60, nx, ny);
        if (R() > 0.42) {
          g.stroke();
          g.beginPath();
          g.moveTo(nx, ny);
          g.lineWidth *= 0.55;
          g.lineTo(nx + (R() - 0.5) * 180, ny + (R() - 0.3) * 120);
          g.stroke();
          g.beginPath();
          g.moveTo(nx, ny);
        }
        x = nx;
        y = ny;
      }
      g.stroke();
    }

    // Crisp beveled perimeter grout joints
    g.fillStyle = s.grout;
    g.fillRect(0, 0, W, 4);
    g.fillRect(0, 0, 4, Hh);
    g.fillStyle = 'rgba(255,255,255,0.65)';
    g.fillRect(4, 4, W - 4, 2);
    g.fillRect(4, 4, 2, Hh - 4);
  } else if (kind === 'terrazzo') {
    const cs = ['#b9a58c', '#8fa3a0', '#c9b7a2', '#a88f76', '#7e8a86', '#ffffff', '#2c3338'];
    for (let k = 0; k < 340; k++) {
      g.fillStyle = cs[k % cs.length];
      g.beginPath();
      g.arc(R() * W, R() * Hh, 2 + R() * 8, 0, Math.PI * 2);
      g.fill();
    }
    if (s.grout) {
      g.fillStyle = s.grout;
      g.fillRect(0, 0, W, 4);
      g.fillRect(0, 0, 4, Hh);
    }
  } else {
    // Porcelain / Slate Ceramic Tiles with subtle micro-texture
    for (let k = 0; k < 1800; k++) {
      g.fillStyle = `rgba(0,0,0,${R() * 0.04})`;
      g.fillRect(R() * W, R() * Hh, 2, 2);
    }
    if (s.grout) {
      g.fillStyle = s.grout;
      g.fillRect(0, 0, W, 5);
      g.fillRect(0, 0, 5, Hh);
      g.fillStyle = 'rgba(255,255,255,0.25)';
      g.fillRect(5, 5, W - 5, 2);
      g.fillRect(5, 5, 2, Hh - 5);
    }
  }

  const t = new THREE.CanvasTexture(cv);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / s.sx, 1 / s.sy);
  t.colorSpace = THREE.SRGBColorSpace;
  if (renderer?.capabilities) {
    t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  }

  return (floorMats[kind] = new THREE.MeshStandardMaterial({
    map: t,
    roughness: s.rough,
    metalness: kind === 'marble' ? 0.05 : 0
  }));
}

// Procedural PBR Wall Materials (Slats, Heritage Plasters, Stone, Linen, Microcement)
export const wallMats = {};

export function wallTextureMat(kind, renderer) {
  if (wallMats[kind]) return wallMats[kind];
  const p = WALL_PAINTS[kind] || WALL_PAINTS.alabaster;

  if (!p.hasTexture) {
    return (wallMats[kind] = new THREE.MeshStandardMaterial({
      color: new THREE.Color(p.sw),
      roughness: p.roughness || 0.88,
      metalness: p.metalness || 0
    }));
  }

  const cv = document.createElement('canvas');
  cv.width = 512;
  cv.height = 512;
  const g = cv.getContext('2d');
  const W = cv.width, Hh = cv.height;
  const R = rng(kind.length * 811 + 37);

  // Fill base color
  g.fillStyle = p.sw;
  g.fillRect(0, 0, W, Hh);

  if (kind === 'wood_slats' || kind === 'walnut_slats') {
    const isWalnut = kind === 'walnut_slats';
    const numSlats = 16;
    const slatW = W / numSlats;
    const gapW = 4;
    const plankW = slatW - gapW;

    for (let i = 0; i < numSlats; i++) {
      const x = i * slatW;
      const toneK = 0.94 + R() * 0.12;
      g.fillStyle = rgbK(p.sw, toneK);
      g.fillRect(x, 0, plankW, Hh);

      // Vertical wood grain lines
      g.strokeStyle = isWalnut ? '#2c1c11' : '#8e6b40';
      g.globalAlpha = 0.28;
      g.lineWidth = 1.0;
      for (let k = 0; k < 4; k++) {
        const gx = x + 2 + R() * (plankW - 4);
        g.beginPath();
        g.moveTo(gx, 0);
        for (let y = 0; y <= Hh; y += 32) {
          g.lineTo(gx + Math.sin(y * 0.03 + k) * 1.5, y);
        }
        g.stroke();
      }
      g.globalAlpha = 1.0;

      // Slat edge highlight
      g.fillStyle = 'rgba(255, 255, 255, 0.15)';
      g.fillRect(x, 0, 1.5, Hh);

      // Deep dark shadow gap between slats
      g.fillStyle = isWalnut ? '#110a06' : '#1c140c';
      g.fillRect(x + plankW, 0, gapW, Hh);
    }
  } else if (kind === 'marble_slab') {
    for (let c = 0; c < 12; c++) {
      const grad = g.createRadialGradient(R() * W, R() * Hh, 20, R() * W, R() * Hh, 240);
      grad.addColorStop(0, 'rgba(240,234,222,0.40)');
      grad.addColorStop(1, 'rgba(252,250,246,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, Hh);
    }
    const veinColors = ['rgba(195,155,95,0.48)', 'rgba(125,120,110,0.38)', 'rgba(215,175,110,0.32)'];
    for (let k = 0; k < 7; k++) {
      g.strokeStyle = veinColors[k % veinColors.length];
      g.lineWidth = 1.5 + R() * 3.5;
      g.beginPath();
      let x = R() * W, y = 0;
      g.moveTo(x, y);
      for (let step = 0; step < 4; step++) {
        const nx = x + (R() - 0.4) * W * 0.5;
        const ny = y + Hh * 0.25;
        g.bezierCurveTo(x + (R() - 0.5) * 80, y + 40, nx + (R() - 0.5) * 80, ny - 40, nx, ny);
        x = nx; y = ny;
      }
      g.stroke();
    }
  } else if (kind === 'najdi_clay') {
    for (let k = 0; k < 2800; k++) {
      const alpha = 0.04 + R() * 0.08;
      g.fillStyle = R() > 0.4 ? `rgba(90, 65, 45, ${alpha})` : `rgba(245, 230, 205, ${alpha})`;
      g.fillRect(R() * W, R() * Hh, 2 + R() * 2, 2 + R() * 2);
    }
    g.strokeStyle = 'rgba(235, 220, 185, 0.55)';
    g.lineWidth = 1.2;
    for (let k = 0; k < 90; k++) {
      const sx = R() * W, sy = R() * Hh;
      const angle = R() * Math.PI;
      const len = 3 + R() * 6;
      g.beginPath();
      g.moveTo(sx, sy);
      g.lineTo(sx + Math.cos(angle) * len, sy + Math.sin(angle) * len);
      g.stroke();
    }
  } else if (kind === 'hejaz_stone') {
    for (let k = 0; k < 2200; k++) {
      g.fillStyle = `rgba(80, 70, 60, ${R() * 0.06})`;
      g.beginPath();
      g.arc(R() * W, R() * Hh, 1 + R() * 3, 0, Math.PI * 2);
      g.fill();
    }
    for (let k = 0; k < 1500; k++) {
      g.fillStyle = `rgba(255, 255, 255, ${R() * 0.08})`;
      g.fillRect(R() * W, R() * Hh, 1.5, 1.5);
    }
  } else if (kind === 'woven_linen') {
    const step = 6;
    g.strokeStyle = 'rgba(120, 105, 85, 0.15)';
    g.lineWidth = 1.0;
    for (let x = 0; x <= W; x += step) {
      g.beginPath(); g.moveTo(x, 0); g.lineTo(x, Hh); g.stroke();
    }
    g.strokeStyle = 'rgba(255, 255, 255, 0.20)';
    for (let y = 0; y <= Hh; y += step) {
      g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke();
    }
    for (let k = 0; k < 1200; k++) {
      g.fillStyle = `rgba(100, 85, 65, ${R() * 0.06})`;
      g.fillRect(R() * W, R() * Hh, 1.5, 1.5);
    }
  } else if (kind === 'microcement') {
    for (let c = 0; c < 14; c++) {
      const grad = g.createRadialGradient(R() * W, R() * Hh, 15, R() * W, R() * Hh, 180);
      grad.addColorStop(0, R() > 0.5 ? 'rgba(160,165,168,0.22)' : 'rgba(235,238,240,0.20)');
      grad.addColorStop(1, 'rgba(203,206,206,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, W, Hh);
    }
    for (let k = 0; k < 1500; k++) {
      g.fillStyle = `rgba(40,45,50,${R() * 0.04})`;
      g.fillRect(R() * W, R() * Hh, 1, 1);
    }
  }

  const t = new THREE.CanvasTexture(cv);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  if (kind === 'wood_slats' || kind === 'walnut_slats') {
    t.repeat.set(2, 1);
  } else if (kind === 'woven_linen') {
    t.repeat.set(4, 4);
  } else if (kind === 'najdi_clay' || kind === 'hejaz_stone' || kind === 'microcement') {
    t.repeat.set(2, 2);
  } else {
    t.repeat.set(1, 1);
  }
  t.colorSpace = THREE.SRGBColorSpace;
  if (renderer?.capabilities) {
    t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  }

  return (wallMats[kind] = new THREE.MeshStandardMaterial({
    map: t,
    roughness: p.roughness || 0.88,
    metalness: p.metalness || 0
  }));
}
