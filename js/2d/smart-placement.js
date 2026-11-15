// Intelligent Furniture Placement & Room/Wall Auto-Orientation
import { ROOMS, DOORS } from '../data/floorplan.js';

export function pointInPoly(pt, poly) {
  const [x, y] = pt;
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const xi = poly[i][0], yi = poly[i][1];
    const xj = poly[j][0], yj = poly[j][1];
    const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function distToSegment(px, py, x1, y1, x2, y2) {
  const dx = x2 - x1, dy = y2 - y1;
  const l2 = dx * dx + dy * dy;
  if (l2 === 0) return Math.hypot(px - x1, py - y1);
  const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / l2));
  return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
}

// Items that naturally belong in the open center of a room rather than wall-mounted
const CENTER_ITEMS = new Set([
  'rug', 'coffeetable', 'sidetable', 'table', 'roundtable',
  'diningchair', 'barstool', 'island', 'armchair', 'beanbag',
  'floorlamp', 'plant', 'treadmill', 'chair', 'officechair'
]);

/**
 * Extracts orthogonal wall segments from a room polygon with interior facing direction
 */
export function getRoomWalls(poly) {
  const walls = [];
  const n = poly.length;
  for (let i = 0; i < n; i++) {
    const [x1, y1] = poly[i];
    const [x2, y2] = poly[(i + 1) % n];
    const hz = Math.abs(y2 - y1) < 2;
    const vt = Math.abs(x2 - x1) < 2;
    if (!hz && !vt) continue;

    const len = hz ? Math.abs(x2 - x1) : Math.abs(y2 - y1);
    if (len < 300) continue; // Skip minor alcoves/notches

    const minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
    const minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
    const midX = (minX + maxX) / 2;
    const midY = (minY + maxY) / 2;

    let rot = 0, side = 'N';
    if (hz) {
      if (pointInPoly([midX, minY + 80], poly)) {
        rot = 0;   // North wall: back touches minY, front faces South (+y)
        side = 'N';
      } else {
        rot = 180; // South wall: back touches maxY, front faces North (-y)
        side = 'S';
      }
    } else {
      if (pointInPoly([minX + 80, midY], poly)) {
        rot = 270; // West wall: back touches minX, front faces East (+x)
        side = 'W';
      } else {
        rot = 90;  // East wall: back touches maxX, front faces West (-x)
        side = 'E';
      }
    }

    walls.push({ hz, minX, maxX, minY, maxY, len, midX, midY, rot, side });
  }
  return walls;
}

/**
 * Computes optimal non-awkward initial placement and rotation for an added furniture item
 */
export function findBestPlacement(it, targetPt, preferredRoomId, existingFurniture = []) {
  const [type, name, w, d, color] = it;
  const isCenter = CENTER_ITEMS.has(type);

  let room = null;
  if (preferredRoomId) {
    room = ROOMS.find(r => r.id === preferredRoomId);
  }
  if (!room && targetPt) {
    room = ROOMS.find(r => pointInPoly([targetPt.x, targetPt.y], r.poly));
  }
  if (!room && targetPt) {
    // Find closest room by distance to centroid
    let minDist = Infinity;
    for (const r of ROOMS) {
      const at = r.at || [r.poly[0][0], r.poly[0][1]];
      const dist = Math.hypot(targetPt.x - at[0], targetPt.y - at[1]);
      if (dist < minDist) {
        minDist = dist;
        room = r;
      }
    }
  }
  if (!room) room = ROOMS[0];

  const poly = room.poly;
  const walls = getRoomWalls(poly);

  // Centerpiece items: place at room centroid or drop location, oriented along room aspect ratio
  if (isCenter || walls.length === 0) {
    let cx = room.at ? room.at[0] : (poly[0][0] + poly[2][0]) / 2;
    let cy = room.at ? room.at[1] : (poly[0][1] + poly[2][1]) / 2;
    let rot = 0;

    if (targetPt && pointInPoly([targetPt.x, targetPt.y], poly)) {
      cx = targetPt.x;
      cy = targetPt.y;
    }

    const xs = poly.map(p => p[0]), ys = poly.map(p => p[1]);
    const rW = Math.max(...xs) - Math.min(...xs);
    const rH = Math.max(...ys) - Math.min(...ys);
    if (w > d && rH > rW * 1.2) rot = 90;

    return { cx: Math.round(cx / 10) * 10, cy: Math.round(cy / 10) * 10, rot, w, d };
  }

  // Wall-bound items: score walls and select optimal unobstructed placement
  let bestWall = null;
  let bestScore = -Infinity;

  for (const wall of walls) {
    let score = wall.len;

    // Penalty if wall is shorter than item width
    if (wall.len < w) score -= 6000;

    // Check door intersection on this wall
    const hasDoor = DOORS.some(dObj => {
      const [x0, y0, x1, y1] = dObj.rect;
      if (wall.hz) {
        return Math.abs(y0 - wall.minY) < 250 && x1 > wall.minX && x0 < wall.maxX;
      } else {
        return Math.abs(x0 - wall.minX) < 250 && y1 > wall.minY && y0 < wall.maxY;
      }
    });
    if (hasDoor) score -= 3500;

    // Penalty for each existing furniture item along this wall
    const furnCount = existingFurniture.filter(f => {
      if (wall.hz) return Math.abs(f.cy - wall.minY) < (f.d + d) / 2 + 150;
      return Math.abs(f.cx - wall.minX) < (f.w + d) / 2 + 150;
    }).length;
    score -= furnCount * 1400;

    // Closeness to targetPt (if user specified a drop point or drag release)
    if (targetPt) {
      const dist = wall.hz
        ? distToSegment(targetPt.x, targetPt.y, wall.minX, wall.minY, wall.maxX, wall.minY)
        : distToSegment(targetPt.x, targetPt.y, wall.minX, wall.minY, wall.minX, wall.maxY);
      score -= dist * 2.5;
    }

    if (score > bestScore) {
      bestScore = score;
      bestWall = wall;
    }
  }

  if (!bestWall) bestWall = walls[0];

  const gap = 15; // 15mm clearance from wall to prevent Z-fighting and geometry penetration
  let cx = 0, cy = 0;
  const rot = bestWall.rot;

  if (bestWall.side === 'N') {
    cy = bestWall.minY + d / 2 + gap;
    const minC = bestWall.minX + w / 2 + 40;
    const maxC = bestWall.maxX - w / 2 - 40;
    cx = targetPt ? Math.max(minC, Math.min(maxC, targetPt.x)) : (minC + maxC) / 2;
  } else if (bestWall.side === 'S') {
    cy = bestWall.maxY - d / 2 - gap;
    const minC = bestWall.minX + w / 2 + 40;
    const maxC = bestWall.maxX - w / 2 - 40;
    cx = targetPt ? Math.max(minC, Math.min(maxC, targetPt.x)) : (minC + maxC) / 2;
  } else if (bestWall.side === 'W') {
    cx = bestWall.minX + d / 2 + gap;
    const minC = bestWall.minY + w / 2 + 40;
    const maxC = bestWall.maxY - w / 2 - 40;
    cy = targetPt ? Math.max(minC, Math.min(maxC, targetPt.y)) : (minC + maxC) / 2;
  } else if (bestWall.side === 'E') {
    cx = bestWall.maxX - d / 2 - gap;
    const minC = bestWall.minY + w / 2 + 40;
    const maxC = bestWall.maxY - w / 2 - 40;
    cy = targetPt ? Math.max(minC, Math.min(maxC, targetPt.y)) : (minC + maxC) / 2;
  }

  return {
    cx: Math.round(cx / 10) * 10,
    cy: Math.round(cy / 10) * 10,
    rot,
    w,
    d
  };
}
