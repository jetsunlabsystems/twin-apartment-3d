import fs from 'fs';

const W_ENVELOPE = 15800; // 15.80m Building Width
const PARTY_X = 7900;     // Center structural party wall
const BOUNDS = { x: -800, y: -800, w: 17400, h: 30600 };

// ==========================================
// 1. ROOMS (Left Apartment)
// ==========================================
const leftRooms = [
  // 1. Master Suite
  {
    id: 'm_bed_l',
    name: 'جناح النوم الرئيسي',
    poly: [[200, 200], [4200, 200], [4200, 5200], [200, 5200]],
    mat: 'wood',
    at: [2200, 2700]
  },
  {
    id: 'm_bath_l',
    name: 'حمام ماستر',
    poly: [[200, 5320], [2140, 5320], [2140, 7120], [200, 7120]],
    mat: 'marble',
    at: [1170, 6220]
  },
  {
    id: 'm_closet_l',
    name: 'ملابس',
    poly: [[2260, 5320], [4200, 5320], [4200, 7120], [2260, 7120]],
    mat: 'wood',
    at: [3230, 6220]
  },

  // 2. Bedroom 2
  {
    id: 'bed2_l',
    name: 'غرفة نوم 2',
    poly: [[4320, 200], [7800, 200], [7800, 4000], [4320, 4000]],
    mat: 'wood',
    at: [6060, 2100]
  },

  // 3. Laundry & Family Bath
  {
    id: 'laund_l',
    name: 'غرفة غسيل',
    poly: [[5800, 4120], [7800, 4120], [7800, 6020], [5800, 6020]],
    mat: 'tile800',
    at: [6800, 5070]
  },
  {
    id: 'cbath_l',
    name: 'حمام عائلي',
    poly: [[5800, 6140], [7800, 6140], [7800, 9540], [5800, 9540]],
    mat: 'antislip',
    at: [6800, 7840]
  },

  // 4. Bedroom 1 (4.29m x 4.00m)
  {
    id: 'bed1_l',
    name: 'غرفة نوم 1',
    poly: [[200, 7240], [4490, 7240], [4490, 11240], [200, 11240]],
    mat: 'wood',
    at: [2345, 9240]
  },

  // 5. Open-Concept Family Living Room (معيشة, 5.60m x 3.60m, open to hall & lightwell)
  {
    id: 'living_l',
    name: 'غرفة المعيشة',
    poly: [[200, 11360], [5840, 11360], [5840, 14960], [200, 14960]],
    mat: 'wood',
    at: [3000, 13160]
  },

  // 6. Kitchen (مطبخ, 4.29m x 3.25m)
  {
    id: 'kitchen_l',
    name: 'المطبخ',
    poly: [[200, 15080], [4490, 15080], [4490, 18330], [200, 18330]],
    mat: 'tile600',
    at: [2345, 16705]
  },

  // 7. Guest Bathroom (حمام ضيوف, 2.50m WC + 1.67m Vanity Anteroom)
  {
    id: 'gbath_l',
    name: 'حمام ضيوف',
    poly: [[200, 18450], [4490, 18450], [4490, 19650], [200, 19650]],
    mat: 'marble',
    at: [2345, 19050]
  },

  // 8. Grand Reception (استقبال, 7.71m width with 1.20m stepped facade)
  {
    id: 'rec_l',
    name: 'صالون الاستقبال',
    poly: [
      [200, 19770], [7800, 19770],
      [7800, 28120], [3990, 28120],
      [3990, 26920], [200, 26920]
    ],
    mat: 'marble',
    at: [4000, 23345]
  },

  // 9. Dedicated Corner Terrace (تراس, strictly 3.79m x 2.00m corner box)
  {
    id: 'terr_l',
    name: 'التراس',
    poly: [
      [200, 26920], [3990, 26920],
      [3990, 28920], [200, 28920]
    ],
    mat: 'terrace',
    at: [2095, 27920],
    counted: false
  }
];

// Mirror rooms for Right Apartment
const rightRooms = leftRooms.map(r => ({
  ...r,
  id: r.id.replace('_l', '_r'),
  poly: r.poly.map(([x, y]) => [W_ENVELOPE - x, y]).reverse(),
  at: [W_ENVELOPE - r.at[0], r.at[1]]
}));

// Common Core: Lightwell (منور), Staircase & Elevator (الدرج والمصعد), Entrance Lobby (مدخل الشقق)
const commonRooms = [
  {
    id: 'shaft_lightwell',
    name: 'منور رئيسي',
    poly: [[5840, 9660], [9960, 9660], [9960, 13230], [5840, 13230]],
    mat: 'antislip',
    at: [7900, 11445],
    counted: false
  },
  {
    id: 'stair_core',
    name: 'الدرج والمصعد',
    poly: [[6040, 13450], [9760, 13450], [9760, 17300], [6040, 17300]],
    mat: 'tile800',
    at: [7900, 15375],
    counted: false
  },
  {
    id: 'entry_lobby',
    name: 'مدخل الشقق الرئيسي',
    poly: [[6040, 17300], [9760, 17300], [9760, 18600], [6040, 18600]],
    mat: 'marble',
    at: [7900, 17950],
    counted: false
  }
];

const ROOMS = [...leftRooms, ...rightRooms, ...commonRooms];

// ==========================================
// 2. DOORS (Exact CAD Hinge & Swing Vectors)
// ==========================================
const leftDoors = [
  // 1. Master Bedroom Door
  {
    name: 'باب جناح النوم الرئيسي',
    rect: [4200, 4250, 4320, 5100],
    h: [4200, 5100],
    c: [0, -1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 2. Master Bed to Dressing Room Door
  {
    name: 'باب غرفة الملابس الماستر',
    rect: [2600, 5200, 3450, 5320],
    h: [2600, 5320],
    c: [1, 0],
    o: [0, 1],
    len: 800,
    entry: false
  },
  // 3. Master Dressing to Master Bath Door
  {
    name: 'باب حمام الماستر',
    rect: [2140, 5400, 2260, 6150],
    h: [2140, 5400],
    c: [0, 1],
    o: [-1, 0],
    len: 750,
    entry: false
  },
  // 4. Bedroom 2 Door
  {
    name: 'باب غرفة نوم 2',
    rect: [4320, 3880, 5170, 4000],
    h: [4320, 4000],
    c: [1, 0],
    o: [0, -1],
    len: 850,
    entry: false
  },
  // 5. Laundry Room Door
  {
    name: 'باب غرفة الغسيل',
    rect: [5680, 4200, 5800, 4950],
    h: [5800, 4200],
    c: [0, 1],
    o: [1, 0],
    len: 750,
    entry: false
  },
  // 6. Family Bathroom Door
  {
    name: 'باب الحمام العائلي',
    rect: [5680, 6250, 5800, 7000],
    h: [5800, 6250],
    c: [0, 1],
    o: [1, 0],
    len: 750,
    entry: false
  },
  // 7. Bedroom 1 Door (from 1.20m hallway into Bed 1)
  {
    name: 'باب غرفة نوم 1',
    rect: [4490, 7350, 4610, 8200],
    h: [4490, 7350],
    c: [0, 1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 8. Kitchen Door (from 1.40m gallery hallway into Kitchen bottom-right)
  {
    name: 'باب المطبخ',
    rect: [4490, 17350, 4610, 18200],
    h: [4490, 18200],
    c: [0, -1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 9. Guest Bathroom Inner Privacy Door (between Vanity Anteroom and WC)
  {
    name: 'باب حمام الضيوف الداخلي',
    rect: [2700, 18550, 2820, 19300],
    h: [2700, 18550],
    c: [0, 1],
    o: [-1, 0],
    len: 750,
    entry: false
  },
  // 10. Apartment Main Entrance Door (hinged at South column, swings into private gallery)
  {
    name: 'مدخل الشقة اليسرى',
    rect: [5920, 17500, 6040, 18450],
    h: [6040, 18450],
    c: [0, -1],
    o: [-1, 0],
    len: 950,
    entry: true
  }
];

// Mirror doors for Right Apartment
const rightDoors = leftDoors.map(d => ({
  name: d.name.replace('اليسرى', 'اليمنى'),
  rect: [W_ENVELOPE - d.rect[2], d.rect[1], W_ENVELOPE - d.rect[0], d.rect[3]],
  h: [W_ENVELOPE - d.h[0], d.h[1]],
  c: [-d.c[0], d.c[1]],
  o: [-d.o[0], d.o[1]],
  len: d.len,
  entry: d.entry
}));

const DOORS = [...leftDoors, ...rightDoors];

// ==========================================
// 3. SLIDING GLASS PATIO DOORS (Terrace Only)
// ==========================================
const SLIDES = [
  { rect: [1200, 26870, 3200, 26970], v: false },
  { rect: [W_ENVELOPE - 3200, 26870, W_ENVELOPE - 1200, 26970], v: false }
];

// ==========================================
// 4. WINDOWS (Facade & Light Openings)
// ==========================================
const leftWins = [
  [1200, 0, 3200, 200, 0.45, 2.4],     // Master Bed North Facade
  [0, 1600, 200, 3600, 0.45, 2.4],     // Master Bed West Exterior
  [5200, 0, 7000, 200, 0.45, 2.4],     // Bedroom 2 North Facade
  [0, 8200, 200, 10200, 0.45, 2.4],    // Bedroom 1 West Exterior
  [0, 12300, 200, 14000, 0.45, 2.4],   // Living Room West Exterior
  [0, 15800, 200, 17400, 0.9, 2.4],    // Kitchen West Exterior
  [0, 21500, 200, 24500, 0.45, 2.4],   // Grand Reception West Window
  [4400, 28000, 7400, 28200, 0.45, 2.4] // Grand Reception South Street Facade (3.80m Window)
];

const rightWins = leftWins.map(w => [
  W_ENVELOPE - w[2], w[1], W_ENVELOPE - w[0], w[3], w[4], w[5]
]);

const WINS = [...leftWins, ...rightWins];

// ==========================================
// 5. WALLS & STRUCTURAL COLUMNS
// ==========================================
const WALLS = [];
function addW(x0, y0, x1, y1, k) {
  const minX = Math.min(x0, x1), maxX = Math.max(x0, x1);
  const minY = Math.min(y0, y1), maxY = Math.max(y0, y1);
  WALLS.push([minX, minY, maxX, maxY, k]);
}

// Concrete Columns (Hatched pillars from CAD Blueprints)
// North Facade columns
addW(0, 0, 400, 400, 'b');
addW(4000, 0, 4400, 400, 'b');
addW(7700, 0, 8100, 400, 'b');
addW(11400, 0, 11800, 400, 'b');
addW(15400, 0, 15800, 400, 'b');

// West & East Perimeter columns
addW(0, 5000, 400, 5400, 'b');
addW(15400, 5000, 15800, 5400, 'b');

addW(0, 7000, 400, 7400, 'b');
addW(15400, 7000, 15800, 7400, 'b');

addW(0, 11100, 400, 11500, 'b');
addW(15400, 11100, 15800, 11500, 'b');

addW(0, 14800, 400, 15200, 'b');
addW(15400, 14800, 15800, 15200, 'b');

addW(0, 19600, 400, 20000, 'b');
addW(15400, 19600, 15800, 20000, 'b');

// Corner columns at terrace entrance
addW(0, 26720, 400, 27120, 'b');
addW(15400, 26720, 15800, 27120, 'b');

// Terrace Inner Corner Column (connecting terrace to 3.80m facade wall)
addW(3800, 26920, 4200, 27320, 'b');
addW(W_ENVELOPE - 4200, 26920, W_ENVELOPE - 3800, 27320, 'b');

// Interior Columns
// Laundry corner column
addW(5600, 3800, 6000, 4200, 'b');
addW(W_ENVELOPE - 6000, 3800, W_ENVELOPE - 5600, 4200, 'b');

// Lightwell (منور) 4 structural columns
addW(5640, 9460, 6040, 9860, 'b');
addW(9760, 9460, 10160, 9860, 'b');
addW(5640, 13030, 6040, 13430, 'b');
addW(9760, 13030, 10160, 13430, 'b');

// Staircase & Lobby columns
addW(5840, 17100, 6240, 17500, 'b');
addW(9560, 17100, 9960, 17500, 'b');
addW(5840, 18400, 6240, 18800, 'b');
addW(9560, 18400, 9960, 18800, 'b');

// 1.20m concrete column at party wall in Grand Reception (marked 1,20 in CAD)
addW(7700, 26920, 8100, 28120, 'b');

// Terrace Outer Corner Columns
addW(0, 28520, 400, 28920, 'b');
addW(15400, 28520, 15800, 28920, 'b');
addW(3800, 28520, 4200, 28920, 'b');
addW(W_ENVELOPE - 4200, 28520, W_ENVELOPE - 3800, 28920, 'b');

// ==========================================
// Exterior Envelope Walls
// ==========================================
// North Exterior
addW(400, 0, 1200, 200, 'e');
addW(3200, 0, 4000, 200, 'e');
addW(4400, 0, 5200, 200, 'e');
addW(7000, 0, 7700, 200, 'e');
addW(8100, 0, 8800, 200, 'e');
addW(10600, 0, 11400, 200, 'e');
addW(11800, 0, 12600, 200, 'e');
addW(14600, 0, 15400, 200, 'e');

// West Exterior
addW(0, 400, 200, 1600, 'e');
addW(0, 3600, 200, 5000, 'e');
addW(0, 5400, 200, 7000, 'e');
addW(0, 7400, 200, 8200, 'e');
addW(0, 10200, 200, 11100, 'e');
addW(0, 11500, 200, 12300, 'e');
addW(0, 14000, 200, 14800, 'e');
addW(0, 15200, 200, 15800, 'e');
addW(0, 17400, 200, 19600, 'e');
addW(0, 20000, 200, 21500, 'e');
addW(0, 24500, 200, 26720, 'e');

// East Exterior (Symmetrical Mirror)
addW(15600, 400, 15800, 1600, 'e');
addW(15600, 3600, 15800, 5000, 'e');
addW(15600, 5400, 15800, 7000, 'e');
addW(15600, 7400, 15800, 8200, 'e');
addW(15600, 10200, 15800, 11100, 'e');
addW(15600, 11500, 15800, 12300, 'e');
addW(15600, 14000, 15800, 14800, 'e');
addW(15600, 15200, 15800, 15800, 'e');
addW(15600, 17400, 15800, 19600, 'e');
addW(15600, 20000, 15800, 21500, 'e');
addW(15600, 24500, 15800, 26720, 'e');

// Central Structural Party Walls
addW(7800, 400, 8000, 9660, 'b');     // Party wall between Bed 2, Laundry, Family Bath
addW(7800, 18600, 8000, 26920, 'b');   // Party wall between Receptions
addW(7800, 26920, 8000, 28120, 'b');   // 1.20m party wall column at facade

// ==========================================
// Left Apartment Interior Partitions
// ==========================================
// Master Suite Partitions
addW(4200, 200, 4320, 4250);          // Master Bed / Bed 2 divider wall (top jamb)
addW(4200, 5100, 4320, 5320);         // Master Bed / Corridor wall (bottom jamb)
addW(200, 5200, 2600, 5320);          // Master Bed South wall (west of Dressing door)
addW(3450, 5200, 4200, 5320);         // Master Bed South wall (east of Dressing door)
addW(2140, 5320, 2260, 5400);         // Master Bath / Closet divider top
addW(2140, 6150, 2260, 7120);         // Master Bath / Closet divider bottom
addW(200, 7120, 4490, 7240);          // Master Suite South wall / Bed 1 North wall
addW(4200, 5320, 4320, 7240);         // Master Closet East wall

// Bedroom 2 Partitions
addW(5170, 4000, 7800, 4120);         // Bed 2 South wall / Laundry North wall
addW(5680, 4120, 5800, 4200);         // Laundry West wall top
addW(5680, 4950, 5800, 6020);         // Laundry West wall bottom
addW(5800, 6020, 7800, 6140);         // Laundry / Family Bath divider
addW(5680, 6140, 5800, 6250);         // Family Bath West wall top
addW(5680, 7000, 5800, 9540);         // Family Bath West wall bottom
addW(5800, 9540, 7800, 9660);         // Family Bath South wall

// Bedroom 1 Partitions (Flush West gallery plane at X = 4490..4610)
addW(4490, 7240, 4610, 7350);         // Bed 1 East wall top jamb
addW(4490, 8200, 4610, 11240);        // Bed 1 East wall bottom
addW(200, 11240, 4610, 11360);        // Bed 1 South wall / Living Room North wall (ends flush at X = 4610!)

// Living Room: COMPLETELY OPEN ON THE EAST (No wall between X=4610 and X=5840!)
addW(200, 14960, 4610, 15080);        // Living Room South wall / Kitchen North wall (ends flush at X = 4610!)

// Kitchen Partitions (Flush West gallery plane at X = 4490..4610)
addW(4490, 15080, 4610, 17350);       // Kitchen East wall top
addW(4490, 18200, 4610, 18330);       // Kitchen East wall bottom jamb
addW(200, 18330, 4610, 18450);        // Kitchen South wall / Guest Bath North wall

// Guest Bathroom Partitions
addW(2700, 18450, 2820, 18550);       // Divider wall top jamb (WC vs. Vanity Anteroom)
addW(2700, 19300, 2820, 19650);       // Divider wall bottom jamb
addW(4490, 18450, 4610, 18600);       // Guest Bath East wall top
addW(4490, 19500, 4610, 19650);       // Guest Bath East wall bottom (open 900mm threshold to vanity!)
addW(200, 19650, 4610, 19770);        // Guest Bath South wall
addW(4610, 19650, 7800, 19770);       // Reception North wall

// Reception South Facade & Terrace Divider Walls
addW(200, 26920, 1200, 27040, 'e');   // Terrace Door left jamb
addW(3200, 26920, 3990, 27040, 'e');  // Terrace Door right jamb
addW(3870, 26920, 3990, 28120, 'e');  // 1.20m Step wall connecting Terrace Door wall to 3.80m Facade

// 3.80m Reception Exterior Facade (Street-Facing Window Wall)
addW(3990, 28000, 4400, 28120, 'e');  // Left jamb of 3.80m window
addW(7400, 28000, 7800, 28120, 'e');  // Right jamb of 3.80m window

// Entrance Lobby Partitions
addW(5920, 17300, 6040, 17500);       // Lobby Left wall top
addW(5920, 18450, 6040, 18600);       // Lobby Left wall bottom

// Central Core Structural Walls
// Lightwell (منور) Perimeter Walls
addW(5840, 9660, 9960, 9780, 'b');    // Lightwell North wall
addW(5840, 13110, 9960, 13230, 'b');  // Lightwell South wall
addW(5840, 9780, 5960, 13110, 'b');   // Lightwell West wall
addW(9840, 9780, 9960, 13110, 'b');   // Lightwell East wall

// Staircase & Elevator Perimeter Walls
addW(6040, 13450, 9760, 13570, 'b');  // Staircase North wall
addW(6040, 17180, 9760, 17300, 'b');  // Staircase South wall
addW(6040, 13570, 6160, 17180, 'b');  // Staircase West wall
addW(9640, 13570, 9760, 17180, 'b');  // Staircase East wall

// Elevator shaft enclosure
addW(7140, 14350, 8660, 14470, 'b');  // Elevator North
addW(7140, 16180, 8660, 16300, 'b');  // Elevator South
addW(7140, 14470, 7260, 16180, 'b');  // Elevator West
addW(8540, 14470, 8660, 16180, 'b');  // Elevator East

// Mirror Partitions for Right Apartment
const leftPartitions = WALLS.slice(27);
leftPartitions.forEach(w => {
  if (w[0] >= 7800 && w[2] <= 8000) return;
  if (w[0] >= 5840 && w[2] <= 9960 && w[1] >= 9660 && w[3] <= 18600) return;
  addW(W_ENVELOPE - w[2], w[1], W_ENVELOPE - w[0], w[3], w[4]);
});

// Dedicated Terrace Low Railings & Balustrades ('low')
addW(200, 26920, 200, 28920, 'low');   // Left Terrace West Railing (2.00m)
addW(200, 28920, 3990, 28920, 'low');  // Left Terrace South Railing (3.79m)
addW(3990, 28120, 3990, 28920, 'low'); // Left Terrace East Railing Return (0.80m)

// Right Terrace (Symmetrical Mirror)
addW(W_ENVELOPE - 200, 26920, W_ENVELOPE - 200, 28920, 'low');   // Right Terrace East Railing (2.00m)
addW(W_ENVELOPE - 3990, 28920, W_ENVELOPE - 200, 28920, 'low');  // Right Terrace South Railing (3.79m)
addW(W_ENVELOPE - 3990, 28120, W_ENVELOPE - 3990, 28920, 'low'); // Right Terrace West Railing Return (0.80m)

// Write out floorplan.js
const outputFloorplan = `// Architectural Floorplan Dataset - 100% Calibrated from Authentic CAD Blueprints
export const BOUNDS = ${JSON.stringify(BOUNDS, null, 2)};

export const ROOMS = ${JSON.stringify(ROOMS, null, 2)};

export const WALLS = ${JSON.stringify(WALLS, null, 2)};

export const WINS = ${JSON.stringify(WINS, null, 2)};

export const DOORS = ${JSON.stringify(DOORS, null, 2)};

export const SLIDES = ${JSON.stringify(SLIDES, null, 2)};

export const R = {};
ROOMS.forEach(r => { R[r.id] = r; });
`;

fs.writeFileSync('js/data/floorplan.js', outputFloorplan, 'utf8');

// ==========================================
// 6. AUTHENTIC CAD FURNITURE (Matching CAD Image 1, 2, 3)
// ==========================================
let fid = 0;
const F = (type, name, cx, cy, w, d, rot = 0, color = '#ddd') => ({
  id: 'f_' + (++fid),
  type,
  name: { zh: name, en: name },
  cx,
  cy,
  w,
  d,
  rot,
  color
});

const defaultFurn = [];

// Helper to add symmetrical furniture for Left & Right apartments
function addTwin(type, name, cx, cy, w, d, rot, color) {
  defaultFurn.push(F(type, name, cx, cy, w, d, rot, color));
  // Symmetrical counterpart in Right apartment
  const mirCx = W_ENVELOPE - cx;
  const mirRot = (360 - rot) % 360;
  defaultFurn.push(F(type, name, mirCx, cy, w, d, mirRot, color));
}

// 1. MASTER BEDROOM: Headboard on North Wall, flanked by nightstands (Image 3)
addTwin('bed', 'سرير ماستر كينج 1.8m', 2200, 1220, 1800, 2000, 0, '#b8c9d9');
addTwin('nightstand', 'كومودينو أيسر', 1100, 450, 450, 400, 0, '#e8dfd3');
addTwin('nightstand', 'كومودينو أيمن', 3300, 450, 450, 400, 0, '#e8dfd3');
addTwin('rug', 'سجادة ماستر فاخرة', 2200, 1800, 2400, 1700, 0, '#d9cfbf');
addTwin('dresser', 'تسريحة ومرآة', 1000, 3800, 1100, 450, 270, '#efe6d8');

// 2. MASTER DRESSING & BATH SUITE (Image 3)
addTwin('wardrobe', 'خزانة ملابس ماستر مدمجة', 3230, 7000, 1800, 600, 1800, '#e2cfb4');
addTwin('vanity', 'مغسلة ديكور رخام', 500, 6220, 900, 520, 270, '#ffffff');
addTwin('toilet', 'مرحاض معلق مودرن', 1600, 7000, 400, 680, 180, '#ffffff');

// 3. BEDROOM 2 (Image 3)
addTwin('bed', 'سرير كوين 1.5m', 6060, 1220, 1500, 2000, 0, '#c9d6df');
addTwin('nightstand', 'كومودينو', 5100, 450, 450, 400, 0, '#e8dfd3');
addTwin('wardrobe', 'دولاب ملابس كبير', 7500, 2600, 1800, 600, 90, '#efe6d8');
addTwin('desk', 'مكتب دراسة وكرسي', 4640, 2600, 1200, 600, 270, '#e2cfb4');

// 4. LAUNDRY ROOM (Image 3)
addTwin('washer', 'غسالة ملابس أوتوماتيك', 7400, 4500, 600, 600, 90, '#e5e7ea');

// 5. FAMILY BATHROOM (Image 3)
addTwin('vanity', 'مغسلة حمام عائلي', 6800, 6420, 1000, 520, 0, '#ffffff');
addTwin('toilet', 'مرحاض معلق', 7500, 7800, 400, 680, 90, '#ffffff');
addTwin('bathtub', 'بانيو استحمام فاخر', 6800, 9100, 1500, 750, 180, '#ffffff');

// 6. BEDROOM 1 (4.29m x 4.00m)
addTwin('bed', 'سرير نوم 1.5m', 2345, 8260, 1500, 2000, 0, '#c9d6df');
addTwin('nightstand', 'كومودينو أيسر', 1100, 7490, 450, 400, 0, '#e8dfd3');
addTwin('nightstand', 'كومودينو أيمن', 3500, 7490, 450, 400, 0, '#e8dfd3');
addTwin('wardrobe', 'دولاب ملابس', 2345, 10900, 1800, 600, 180, '#efe6d8');
addTwin('desk', 'مكتب دراسة', 4100, 9800, 1200, 600, 90, '#e2cfb4');

// 7. OPEN FAMILY LIVING ROOM (معيشة, 5.60m x 3.60m)
addTwin('sofa', 'كنبة معيشة عائلية L-Shape', 2000, 13160, 2800, 1000, 0, '#7c93a8');
addTwin('tvstand', 'طاولة تلفزيون معيشة', 2000, 14660, 1800, 400, 180, '#d1c4b2');
addTwin('rug', 'سجادة غرفة المعيشة', 2000, 13160, 2400, 1800, 0, '#e5ded5');

// 8. KITCHEN (4.29m x 3.25m)
addTwin('counter', 'كاونتر مطبخ رئيسي رخام', 2345, 15380, 2400, 600, 0, '#ffffff');
addTwin('stove', 'بوتاجاز مسطح', 3800, 15380, 750, 450, 0, '#2b2824');
addTwin('fridge', 'ثلاجة دولابي', 800, 17900, 910, 700, 270, '#c8cbd0');

// 9. GUEST BATH (2.50m WC + 1.67m Vanity Anteroom)
addTwin('vanity', 'مغسلة ضيوف ديكور رخام', 3800, 19050, 900, 520, 0, '#ffffff');
addTwin('toilet', 'مرحاض ضيوف معلق', 1450, 19050, 400, 680, 270, '#ffffff');

// 10. GRAND RECEPTION (7.71m x 7.15m)
addTwin('sofa', 'كنبة استقبال فاخرة 3 مقاعد', 700, 23345, 2400, 900, 270, '#b7c4b0');
addTwin('sofa', 'كنبة ثنائية متناسقة', 4000, 20920, 1800, 880, 0, '#c3cbd6');
addTwin('armchair', 'كرسي فوتيه مذهب', 4000, 25720, 850, 850, 180, '#d6b99a');
addTwin('rug', 'سجادة صالون استقبال كبرى', 2400, 23345, 3000, 2000, 270, '#d9cbb8');
addTwin('coffeetable', 'طاولة قهوة كالاتا رخام', 2400, 23345, 1300, 650, 270, '#e8dccb');
addTwin('tvstand', 'وحدة تلفزيون جدارية فاخرة', 7500, 23345, 2400, 400, 90, '#e2cfb4');

// 11. DEDICATED CORNER TERRACE (Strictly 3.79m x 2.00m)
addTwin('plant', 'نبات زينة للتراس', 800, 28520, 500, 500, 0, '#9dbb8c');

const outputFurn = `// Default Furniture Dataset - 100% Calibrated from Authentic CAD Blueprint
export function defaultFurniture() {
  return ${JSON.stringify(defaultFurn, null, 2)};
}
`;

fs.writeFileSync('js/data/default-furniture.js', outputFurn, 'utf8');

console.log('Build completed successfully!');
console.log(`Rooms: ${ROOMS.length}, Walls: ${WALLS.length}, Doors: ${DOORS.length}, Furniture: ${defaultFurn.length}`);
