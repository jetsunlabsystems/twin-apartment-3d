// Electrical Sockets & Outlets Engineering Dataset & Automation
// Standards: Saudi Building Code (SBC) & IEC 60364-7-701 electrical installations

export const SOCKET_TYPES = {
  duplex: {
    id: 'duplex',
    name: { zh: 'فيش مزدوج 220V', en: 'Duplex Socket 220V' },
    desc: { zh: 'مقبس طاقة مزدوج 13A/16A للأجهزة العامة والشواحن', en: 'Dual 13A/16A power socket for general appliances & chargers' },
    color: '#0284c7',
    defaultHeight: '+30cm',
    icon: '⚡'
  },
  media: {
    id: 'media',
    name: { zh: 'مجمع شاشة وبيانات', en: 'TV & Data Media Cluster' },
    desc: { zh: 'فيش طاقة + مخرج شاشة TV + شبكة إنترنت RJ45 + ماسورة HDMI', en: 'Power + TV Coaxial + Cat6 LAN + HDMI conduit' },
    color: '#ea580c',
    defaultHeight: '+120cm',
    icon: '📺'
  },
  appliance: {
    id: 'appliance',
    name: { zh: 'فيش أجهزة ثقيلة 16A/20A', en: 'Heavy Appliance Outlet' },
    desc: { zh: 'مقبس مخصص للثلاجة، المايكروويف، الفرن، أو غسالة الملابس', en: 'Dedicated heavy circuit for fridge, oven, microwave, or washer' },
    color: '#dc2626',
    defaultHeight: '+110cm',
    icon: '🍳'
  },
  waterproof: {
    id: 'waterproof',
    name: { zh: 'مقبس مقاوم للرطوبة IP44', en: 'Waterproof Socket IP44' },
    desc: { zh: 'مقبس بغطاء حماية مانع لرذاذ الماء للحمامات والمطابخ', en: 'Splash-proof covered socket for bathrooms and kitchen counters' },
    color: '#0d9488',
    defaultHeight: '+110cm',
    icon: '💧'
  },
  ac: {
    id: 'ac',
    name: { zh: 'مفتاح ومقبس تكييف 20A/30A', en: 'AC Disconnect / Outlet' },
    desc: { zh: 'مفتاح عزل ومقبس قدرة عالية لوحدات التكييف الاسبليت', en: 'High capacity isolator point for split air conditioning units' },
    color: '#0891b2',
    defaultHeight: '+220cm',
    icon: '❄️'
  },
  switch: {
    id: 'switch',
    name: { zh: 'مفتاح إنارة ذكي / مزدوج', en: 'Lighting Switch' },
    desc: { zh: 'مفتاح تشغيل الإنارة عند مداخل الغرف والصالونات', en: 'Wall light switch beside room entrance doors' },
    color: '#475569',
    defaultHeight: '+120cm',
    icon: '💡'
  }
};

export const SOCKET_HEIGHTS = [
  { value: '+30cm', label: { zh: '+30cm (أرضي عام)', en: '+30cm (Standard Low)' } },
  { value: '+65cm', label: { zh: '+65cm (فوق الكومودينو)', en: '+65cm (Bedside Table)' } },
  { value: '+110cm', label: { zh: '+110cm (كاونتر / تسريحة / غسالة)', en: '+110cm (Countertop / Vanity)' } },
  { value: '+120cm', label: { zh: '+120cm (مفاتيح ومرايا)', en: '+120cm (Switches & Mirror)' } },
  { value: '+140cm', label: { zh: '+140cm (شاشة جدارية)', en: '+140cm (Wall-Mounted TV)' } },
  { value: '+220cm', label: { zh: '+220cm (تكييف وسخان)', en: '+220cm (AC Unit / High)' } }
];

/**
 * Returns point projected onto the closest segment of a room's polygon
 */
export function projectPointToPoly(pt, poly) {
  let bestPt = null, bestDist = Infinity, bestAngle = 0, bestNormal = 0;
  const n = poly.length;

  for (let i = 0; i < n; i++) {
    const p1 = poly[i], p2 = poly[(i + 1) % n];
    const dx = p2[0] - p1[0], dy = p2[1] - p1[1];
    const lenSq = dx * dx + dy * dy;
    if (lenSq === 0) continue;

    // Projection factor t along segment p1->p2
    let t = ((pt[0] - p1[0]) * dx + (pt[1] - p1[1]) * dy) / lenSq;
    t = Math.max(0.04, Math.min(0.96, t)); // Keep away from extreme corners

    const qx = p1[0] + t * dx;
    const qy = p1[1] + t * dy;
    const dSq = (pt[0] - qx) ** 2 + (pt[1] - qy) ** 2;

    if (dSq < bestDist) {
      bestDist = dSq;
      bestPt = [Math.round(qx), Math.round(qy)];
      bestAngle = Math.atan2(dy, dx) * 180 / Math.PI;
      // Inward normal
      bestNormal = bestAngle + 90;
    }
  }
  return { pt: bestPt, dist: Math.sqrt(bestDist), angle: bestAngle, normal: bestNormal };
}

/**
 * Smart Auto-Generation of Sockets based on Furniture Layout & Architecture
 */
export function autoGenerateSockets(furniture, rooms, walls) {
  const sockets = [];
  let sid = 1;

  const roomMap = {};
  rooms.forEach(r => { roomMap[r.id] = r; });

  const addSocket = (type, x, y, height, roomId, label, rot = 0) => {
    // Avoid duplicate sockets in immediate proximity (< 350mm)
    const exists = sockets.some(s => (s.x - x) ** 2 + (s.y - y) ** 2 < 350 ** 2);
    if (!exists) {
      sockets.push({
        id: 'sk_' + (sid++),
        type,
        x,
        y,
        height: height || SOCKET_TYPES[type].defaultHeight,
        roomId,
        label,
        rot: Math.round(rot)
      });
    }
  };

  // 1. Process furniture items and generate associated sockets
  furniture.forEach(f => {
    // Determine which room this furniture belongs to
    let r = rooms.find(rm => {
      const xs = rm.poly.map(p => p[0]), ys = rm.poly.map(p => p[1]);
      return f.cx >= Math.min(...xs) - 50 && f.cx <= Math.max(...xs) + 50 &&
             f.cy >= Math.min(...ys) - 50 && f.cy <= Math.max(...ys) + 50;
    });
    if (!r) return;

    const proj = projectPointToPoly([f.cx, f.cy], r.poly);
    if (!proj.pt) return;

    const type = f.type;
    const isMaster = r.id.includes('m_bed');
    const isLiving = r.id.includes('living') || r.id.includes('rec');

    // Bed -> Bedside table outlets (+65cm) on headboard wall
    if (type === 'bed') {
      const bedW = f.w || 1800;
      // Left nightstand
      const leftPt = [f.cx - (bedW / 2 + 350), f.cy];
      const pL = projectPointToPoly(leftPt, r.poly);
      if (pL.pt) addSocket('duplex', pL.pt[0], pL.pt[1], '+65cm', r.id, 'فيش كومودينو يمين', pL.normal);

      // Right nightstand
      const rightPt = [f.cx + (bedW / 2 + 350), f.cy];
      const pR = projectPointToPoly(rightPt, r.poly);
      if (pR.pt) addSocket('duplex', pR.pt[0], pR.pt[1], '+65cm', r.id, 'فيش كومودينو يسار', pR.normal);
    }
    // TV Stand -> Media Cluster (+120cm) + Auxiliary Duplex (+30cm)
    else if (type === 'tvstand') {
      addSocket('media', proj.pt[0], proj.pt[1], '+120cm', r.id, 'مجمع شاشة وسينما', proj.normal);
      // Extra socket for soundbar/receiver
      const offX = proj.pt[0] + (proj.angle === 0 ? 450 : 0);
      const offY = proj.pt[1] + (proj.angle !== 0 ? 450 : 0);
      addSocket('duplex', offX, offY, '+30cm', r.id, 'أجهزة صوتية واستقبال', proj.normal);
    }
    // Sofa -> Convenience charging sockets at sofa ends (+30cm)
    else if (type === 'sofa' || type === 'cornersofa') {
      addSocket('duplex', proj.pt[0], proj.pt[1], '+30cm', r.id, 'فيش جلسة وشاحن', proj.normal);
    }
    // Desk -> Study / Computer power & data (+75cm)
    else if (type === 'desk' || type === 'execdesk') {
      addSocket('duplex', proj.pt[0], proj.pt[1], '+65cm', r.id, 'مكتب كمبيوتر', proj.normal);
    }
    // Dresser -> Vanity & Hairdryer (+110cm)
    else if (type === 'dresser') {
      addSocket('duplex', proj.pt[0], proj.pt[1], '+110cm', r.id, 'تسريحة واستشوار', proj.normal);
    }
    // Refrigerator -> Dedicated heavy circuit (+120cm)
    else if (type === 'fridge') {
      addSocket('appliance', proj.pt[0], proj.pt[1], '+120cm', r.id, 'ثلاجة رئيسية', proj.normal);
    }
    // Stove -> Heavy cooker circuit (+60cm)
    else if (type === 'stove') {
      addSocket('appliance', proj.pt[0], proj.pt[1], '+110cm', r.id, 'فرن وموقد كهربائي', proj.normal);
    }
    // Countertop / Kitchen Sink -> Countertop appliances & waterproof
    else if (type === 'counter' || type === 'island' || type === 'ksink') {
      addSocket('waterproof', proj.pt[0], proj.pt[1], '+110cm', r.id, 'كاونتر أجهزة مطبخ', proj.normal);
    }
  });

  // 2. Room-specific essential architectural infrastructure
  rooms.forEach(r => {
    if (!r.poly || r.counted === false) return;
    const xs = r.poly.map(p => p[0]), ys = r.poly.map(p => p[1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);

    // AC Unit Point (+220cm) for bedrooms, living rooms, and salons
    if (['m_bed_l', 'm_bed_r', 'bed1_l', 'bed1_r', 'bed2_l', 'bed2_r', 'living_l', 'living_r', 'rec_l', 'rec_r'].includes(r.id)) {
      // Place AC on north or exterior wall
      const acX = Math.round(minX + (maxX - minX) * 0.75);
      const acPt = projectPointToPoly([acX, minY + 100], r.poly);
      if (acPt.pt) addSocket('ac', acPt.pt[0], acPt.pt[1], '+220cm', r.id, 'نقطة تكييف اسبليت', acPt.normal);
    }

    // Bathroom Waterproof Shaver & Heater Outlets (+120cm)
    if (r.id.includes('bath')) {
      const sinkPt = projectPointToPoly([minX + (maxX - minX) * 0.3, minY + 150], r.poly);
      if (sinkPt.pt) addSocket('waterproof', sinkPt.pt[0], sinkPt.pt[1], '+120cm', r.id, 'مرآة ومغسلة IP44', sinkPt.normal);
    }

    // Laundry Room Washing Machine & Dryer Heavy Waterproof Outlets
    if (r.id.includes('laund')) {
      const wPt = projectPointToPoly([minX + (maxX - minX) * 0.5, maxY - 150], r.poly);
      if (wPt.pt) addSocket('appliance', wPt.pt[0], wPt.pt[1], '+110cm', r.id, 'غسالة ومجفف ملابس', wPt.normal);
    }

    // Light Switch near entrance (+120cm)
    // Approximate entrance at bottom edge of room
    const swPt = projectPointToPoly([minX + 350, maxY - 50], r.poly);
    if (swPt.pt) addSocket('switch', swPt.pt[0], swPt.pt[1], '+120cm', r.id, 'مفتاح إنارة الغرفة', swPt.normal);

    // General Vacuum / Cleaner Convenience Socket (+30cm) for large rooms
    if (r.id.includes('rec') || r.id.includes('living')) {
      const convPt = projectPointToPoly([maxX - 400, minY + 400], r.poly);
      if (convPt.pt) addSocket('duplex', convPt.pt[0], convPt.pt[1], '+30cm', r.id, 'فيش نظافة ومكنسة', convPt.normal);
    }
  });

  return sockets;
}

/**
 * Generates the professional SVG symbol for a socket
 */
export function socketSymbolSVG(s, isSelected) {
  const meta = SOCKET_TYPES[s.type] || SOCKET_TYPES.duplex;
  const col = meta.color;
  const h = s.height || '+30cm';
  const selGlow = isSelected ? `stroke="#f59e0b" stroke-width="3" filter="drop-shadow(0 0 6px #f59e0b)"` : '';

  let sym = '';
  switch (s.type) {
    case 'media':
      sym = `
        <rect x="-90" y="-70" width="180" height="140" rx="20" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <rect x="-65" y="-50" width="130" height="80" rx="10" fill="${col}" opacity="0.15"/>
        <circle cx="-35" cy="-10" r="14" fill="${col}"/>
        <circle cx="35" cy="-10" r="14" fill="${col}"/>
        <text x="0" y="52" font-family="'Tajawal', sans-serif" font-size="34" font-weight="800" fill="${col}" text-anchor="middle">TV/LAN</text>
      `;
      break;

    case 'appliance':
      sym = `
        <circle cx="0" cy="0" r="75" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <path d="M 0 0 L 75 0 A 75 75 0 0 1 0 75 Z" fill="${col}"/>
        <circle cx="-25" cy="-20" r="14" fill="${col}"/>
        <circle cx="25" cy="-20" r="14" fill="${col}"/>
        <text x="0" y="44" font-family="'Tajawal', sans-serif" font-size="36" font-weight="900" fill="${col}" text-anchor="middle">16A</text>
      `;
      break;

    case 'waterproof':
      sym = `
        <circle cx="0" cy="0" r="75" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <circle cx="0" cy="0" r="58" fill="none" stroke="${col}" stroke-width="1.8" stroke-dasharray="5 3"/>
        <circle cx="-25" cy="-10" r="13" fill="${col}"/>
        <circle cx="25" cy="-10" r="13" fill="${col}"/>
        <text x="0" y="44" font-family="'Tajawal', sans-serif" font-size="32" font-weight="800" fill="${col}" text-anchor="middle">IP44</text>
      `;
      break;

    case 'ac':
      sym = `
        <circle cx="0" cy="0" r="75" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <circle cx="-25" cy="0" r="13" fill="${col}"/>
        <circle cx="25" cy="0" r="13" fill="${col}"/>
        <line x1="0" y1="-65" x2="0" y2="65" stroke="${col}" stroke-width="2"/>
        <text x="0" y="45" font-family="'Tajawal', sans-serif" font-size="38" font-weight="900" fill="${col}" text-anchor="middle">AC</text>
      `;
      break;

    case 'switch':
      sym = `
        <circle cx="0" cy="0" r="60" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <line x1="0" y1="0" x2="65" y2="-65" stroke="${col}" stroke-width="3" stroke-linecap="round"/>
        <circle cx="0" cy="0" r="16" fill="${col}"/>
      `;
      break;

    case 'duplex':
    default:
      sym = `
        <circle cx="0" cy="0" r="75" fill="#ffffff" stroke="${col}" stroke-width="2.5" ${selGlow}/>
        <circle cx="-25" cy="-15" r="15" fill="${col}"/>
        <circle cx="25" cy="-15" r="15" fill="${col}"/>
        <line x1="-55" y1="20" x2="55" y2="20" stroke="${col}" stroke-width="2"/>
        <line x1="0" y1="20" x2="0" y2="55" stroke="${col}" stroke-width="2.5"/>
      `;
      break;
  }

  // Generous hit-target so users can easily hover and click without precision pixel hunting
  const hitTarget = `
    <circle cx="0" cy="0" r="140" fill="transparent" pointer-events="all"/>
    <rect x="-80" y="70" width="160" height="70" rx="20" fill="transparent" pointer-events="all"/>
  `;

  // Elevation badge pill
  const badge = `
    <g transform="translate(0, 105)" pointer-events="all">
      <rect x="-65" y="-18" width="130" height="36" rx="18" fill="#0f172a" opacity="0.92"/>
      <text x="0" y="6" font-family="'Tajawal', sans-serif" font-size="24" font-weight="700" fill="#f8fafc" text-anchor="middle">${h}</text>
    </g>
  `;

  return `
    <g class="socket-node ${isSelected ? 'selected' : ''}" data-skid="${s.id}" transform="translate(${s.x}, ${s.y}) rotate(${s.rot || 0})" style="cursor:pointer">
      ${hitTarget}
      ${sym}
      ${badge}
    </g>
  `;
}

/**
 * Computes quantity schedule table breakdown
 */
export function calculateSocketSchedule(sockets, rooms) {
  const roomMap = {};
  rooms.forEach(r => { roomMap[r.id] = r.name; });

  const summary = {
    total: sockets.length,
    byType: { duplex: 0, media: 0, appliance: 0, waterproof: 0, ac: 0, switch: 0 },
    byRoom: {}
  };

  sockets.forEach(s => {
    summary.byType[s.type] = (summary.byType[s.type] || 0) + 1;
    const rName = roomMap[s.roomId] || 'أخرى';
    if (!summary.byRoom[rName]) {
      summary.byRoom[rName] = { duplex: 0, media: 0, appliance: 0, waterproof: 0, ac: 0, switch: 0, total: 0 };
    }
    summary.byRoom[rName][s.type] = (summary.byRoom[rName][s.type] || 0) + 1;
    summary.byRoom[rName].total++;
  });

  return summary;
}
