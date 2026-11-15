// Procedural Canvas Textures for PBR Architectural Flooring
import * as THREE from 'three';
import { rng, rgbK } from '../config.js';

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
