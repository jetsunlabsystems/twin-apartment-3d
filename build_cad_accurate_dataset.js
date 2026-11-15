import fs from 'fs';

const W_ENVELOPE = 15800; // 15.80m Building Width
const PARTY_X = 7900;     // Center structural party wall
const BOUNDS = { x: -800, y: -800, w: 17400, h: 26800 };

// ==========================================
// 1. ROOMS (Left Apartment)
// ==========================================
const leftRooms = [
  {
    id: 'm_bed_l',
    name: 'جناح النوم الرئيسي',
    poly: [[200, 200], [4200, 200], [4200, 5200], [200, 5200]],
    mat: 'wood',
    at: [2200, 2700]
  },
  {
    id: 'bed2_l',
    name: 'غرفة نوم 2',
    poly: [[4320, 200], [7800, 200], [7800, 4000], [4320, 4000]],
    mat: 'wood',
    at: [6060, 2100]
  },
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
  {
    id: 'bed1_l',
    name: 'غرفة نوم 1',
    poly: [[200, 7240], [4200, 7240], [4200, 11240], [200, 11240]],
    mat: 'wood',
    at: [2200, 9240]
  },
  {
    id: 'kitchen_l',
    name: 'المطبخ',
    poly: [[200, 11360], [4200, 11360], [4200, 14610], [200, 14610]],
    mat: 'tile600',
    at: [2200, 12985]
  },
  {
    id: 'gbath_l',
    name: 'حمام ضيوف',
    poly: [[200, 14730], [2700, 14730], [2700, 15930], [200, 15930]],
    mat: 'marble',
    at: [1450, 15330]
  },
  {
    id: 'rec_l',
    name: 'صالون الاستقبال',
    poly: [[200, 16050], [7800, 16050], [7800, 23200], [200, 23200]],
    mat: 'marble',
    at: [4000, 19625]
  },
  {
    id: 'terr_l',
    name: 'التراس',
    poly: [
      [200, 23200], [7800, 23200],
      [7800, 24400], [3990, 24400],
      [3990, 25200], [200, 25200]
    ],
    mat: 'terrace',
    at: [2095, 24200],
    counted: false
  }
];

const rightRooms = leftRooms.map(r => ({
  ...r,
  id: r.id.replace('_l', '_r'),
  poly: r.poly.map(([x, y]) => [W_ENVELOPE - x, y]).reverse(),
  at: [W_ENVELOPE - r.at[0], r.at[1]]
}));

const commonRooms = [
  {
    id: 'entry_lobby',
    name: 'مدخل الشقق الرئيسي',
    poly: [[6040, 14630], [9760, 14630], [9760, 15930], [6040, 15930]],
    mat: 'marble',
    at: [7900, 15280]
  }
];

const ROOMS = [...leftRooms, ...rightRooms, ...commonRooms];

// ==========================================
// 2. DOORS (Exact CAD Hinge & Swing Vectors)
// ==========================================
const leftDoors = [
  // 1. Entrance Door into Left Apartment Foyer
  {
    name: 'مدخل الشقة اليسرى',
    rect: [5920, 14800, 6040, 15800],
    h: [6040, 15750],
    c: [0, -1],
    o: [-1, 0],
    len: 950,
    entry: true
  },
  // 2. Master Bedroom Door (enters from 1.48m corridor, swings inward into master room)
  {
    name: 'باب جناح النوم الرئيسي',
    rect: [4200, 4250, 4320, 5150],
    h: [4200, 5100],
    c: [0, -1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 3. Master Bed to Dressing Room Door (En-Suite Entrance)
  {
    name: 'باب غرفة الملابس الماستر',
    rect: [2600, 5200, 3450, 5320],
    h: [2600, 5320],
    c: [1, 0],
    o: [0, 1],
    len: 800,
    entry: false
  },
  // 4. Master Dressing to Master Bath Door
  {
    name: 'باب حمام الماستر',
    rect: [2140, 5400, 2260, 6200],
    h: [2140, 5400],
    c: [0, 1],
    o: [-1, 0],
    len: 750,
    entry: false
  },
  // 5. Bedroom 2 Door (bottom-left corner, swings inward into Bed 2 against west wall)
  {
    name: 'باب غرفة نوم 2',
    rect: [4320, 3880, 5220, 4000],
    h: [4320, 4000],
    c: [1, 0],
    o: [0, -1],
    len: 850,
    entry: false
  },
  // 6. Laundry Room Door (swings inward into laundry)
  {
    name: 'باب غرفة الغسيل',
    rect: [5680, 4200, 5800, 5000],
    h: [5800, 4200],
    c: [0, 1],
    o: [1, 0],
    len: 750,
    entry: false
  },
  // 7. Family Bathroom Door (swings inward into bathroom)
  {
    name: 'باب الحمام العائلي',
    rect: [5680, 6250, 5800, 7050],
    h: [5800, 6250],
    c: [0, 1],
    o: [1, 0],
    len: 750,
    entry: false
  },
  // 8. Bedroom 1 Door (enters from corridor, swings inward)
  {
    name: 'باب غرفة نوم 1',
    rect: [4200, 7350, 4320, 8250],
    h: [4200, 7350],
    c: [0, 1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 9. Kitchen Door (enters from circulation hallway into kitchen)
  {
    name: 'باب المطبخ',
    rect: [4200, 13650, 4320, 14550],
    h: [4200, 14550],
    c: [0, -1],
    o: [-1, 0],
    len: 850,
    entry: false
  },
  // 10. Guest Bathroom Door (enters from hallway into powder room)
  {
    name: 'باب حمام الضيوف',
    rect: [1800, 15930, 2600, 16050],
    h: [2600, 15930],
    c: [-1, 0],
    o: [0, -1],
    len: 750,
    entry: false
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
// 3. SLIDING GLASS PATIO DOORS (Terrace)
// ==========================================
const SLIDES = [
  { rect: [1000, 23150, 3200, 23250], v: false },
  { rect: [4800, 23150, 7000, 23250], v: false },
  { rect: [W_ENVELOPE - 7000, 23150, W_ENVELOPE - 4800, 23250], v: false },
  { rect: [W_ENVELOPE - 3200, 23150, W_ENVELOPE - 1000, 23250], v: false }
];

// ==========================================
// 4. WINDOWS (Facade & Light Openings)
// ==========================================
const leftWins = [
  [1200, 0, 3200, 200, 0.45, 2.4],     // Master Bed North Facade
  [0, 1600, 200, 3600, 0.45, 2.4],     // Master Bed West Exterior
  [5200, 0, 7000, 200, 0.45, 2.4],     // Bedroom 2 North Facade
  [0, 8200, 200, 10200, 0.45, 2.4],    // Bedroom 1 West Exterior
  [0, 12200, 200, 13800, 0.9, 2.4],    // Kitchen West Exterior
  [0, 18000, 200, 21000, 0.45, 2.4]    // Grand Reception West Window
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

// Concrete Columns (Hatched pillars from CAD Image 1, 2 & 3)
addW(0, 0, 400, 400, 'b');
addW(4000, 0, 4400, 400, 'b');
addW(7700, 0, 8100, 400, 'b');
addW(11400, 0, 11800, 400, 'b');
addW(15400, 0, 15800, 400, 'b');

addW(0, 5000, 400, 5400, 'b');
addW(15400, 5000, 15800, 5400, 'b');

// Column at Laundry / Corridor corner (visible in CAD Image 3!)
addW(5600, 3800, 6000, 4200, 'b');
addW(W_ENVELOPE - 6000, 3800, W_ENVELOPE - 5600, 4200, 'b');

addW(0, 6800, 400, 7200, 'b');
addW(15400, 6800, 15800, 7200, 'b');

addW(0, 11000, 400, 11400, 'b');
addW(15400, 11000, 15800, 11400, 'b');

addW(0, 16000, 400, 16400, 'b');
addW(15400, 16000, 15800, 16400, 'b');

// 1.20m concrete column at party wall in Grand Reception (marked 1,20 in CAD Image 1!)
addW(7700, 19500, 8100, 20700, 'b');

// South exterior corner columns
addW(0, 22800, 400, 23200, 'b');
addW(15400, 22800, 15800, 23200, 'b');

// North Facade Envelope
addW(400, 0, 1200, 200, 'e');
addW(3200, 0, 4000, 200, 'e');
addW(4400, 0, 5200, 200, 'e');
addW(7000, 0, 7700, 200, 'e');
addW(8100, 0, 8800, 200, 'e');
addW(10600, 0, 11400, 200, 'e');
addW(11800, 0, 12600, 200, 'e');
addW(14600, 0, 15400, 200, 'e');

// West Exterior Envelope
addW(0, 400, 200, 1600, 'e');
addW(0, 3600, 200, 5000, 'e');
addW(0, 5400, 200, 6800, 'e');
addW(0, 7200, 200, 8200, 'e');
addW(0, 10200, 200, 11000, 'e');
addW(0, 11400, 200, 12200, 'e');
addW(0, 13800, 200, 16000, 'e');
addW(0, 16400, 200, 18000, 'e');
addW(0, 21000, 200, 22800, 'e');

// East Exterior Envelope
addW(15600, 400, 15800, 1600, 'e');
addW(15600, 3600, 15800, 5000, 'e');
addW(15600, 5400, 15800, 6800, 'e');
addW(15600, 7200, 15800, 8200, 'e');
addW(15600, 10200, 15800, 11000, 'e');
addW(15600, 11400, 15800, 12200, 'e');
addW(15600, 13800, 15800, 16000, 'e');
addW(15600, 16400, 15800, 18000, 'e');
addW(15600, 21000, 15800, 22800, 'e');

// Central Structural Party Wall between Twin Apartments
addW(7800, 400, 8000, 14630, 'b');
addW(7800, 15930, 8000, 19500, 'b');
addW(7800, 20700, 8000, 23200, 'b');

// Left Apartment Partitions
addW(4200, 200, 4320, 4250);          // Master Bed / Bed 2 divider wall (top jamb of Master door)
addW(4200, 5150, 4320, 5320);         // Master Bed / Corridor wall (bottom jamb of Master door)
addW(5220, 4000, 7800, 4120);         // Bed 2 South wall / Laundry North wall (east of Bed 2 door)

addW(5680, 4120, 5800, 4200);         // Laundry West wall top
addW(5680, 5000, 5800, 6020);         // Laundry West wall bottom
addW(5800, 6020, 7800, 6140);         // Laundry / Family Bath divider
addW(5680, 6140, 5800, 6250);         // Family Bath West wall top
addW(5680, 7050, 5800, 9540);         // Family Bath West wall bottom
addW(5800, 9540, 7800, 9660);         // Family Bath South wall

addW(200, 5200, 2600, 5320);          // Master Bed South wall (west of Dressing door)
addW(3450, 5200, 4200, 5320);         // Master Bed South wall (east of Dressing door)
addW(2140, 5320, 2260, 5400);         // Master Bath / Closet divider top
addW(2140, 6200, 2260, 7120);         // Master Bath / Closet divider bottom
addW(200, 7120, 4200, 7240);          // Master Suite South wall / Bed 1 North wall
addW(4200, 5320, 4320, 7350);         // Master Closet East wall
addW(4200, 8250, 4320, 11240);        // Bed 1 East wall
addW(200, 11240, 4200, 11360);        // Bed 1 / Kitchen divider
addW(4200, 11360, 4320, 13650);       // Kitchen East wall top
addW(4200, 14550, 4320, 14730);       // Kitchen East wall bottom
addW(200, 14610, 4200, 14730);        // Kitchen South wall
addW(2700, 14730, 2820, 15930);       // Guest Bath East wall
addW(200, 15930, 1800, 16050);        // Guest Bath South wall
addW(2600, 15930, 4200, 16050);       // Reception North wall west
addW(4200, 15930, 7800, 16050);       // Reception North wall east

// Entrance Lobby Walls
addW(5920, 14630, 6040, 14800);       // Lobby Left wall top
addW(5920, 15800, 6040, 15930);       // Lobby Left wall bottom
addW(6040, 14510, 9760, 14630, 'b');  // Lobby North wall

// Mirror Partitions for Right Apartment
const leftPartitions = WALLS.slice(18);
leftPartitions.forEach(w => {
  if (w[0] >= 7800 && w[2] <= 8000) return;
  if (w[0] >= 5920 && w[2] <= 9760 && w[1] >= 14510 && w[3] <= 14630) return;
  addW(W_ENVELOPE - w[2], w[1], W_ENVELOPE - w[0], w[3], w[4]);
});

// Terrace Walls & Balustrades ('low')
addW(200, 23200, 200, 25200, 'low');
addW(200, 25200, 3990, 25200, 'low');
addW(3990, 24400, 3990, 25200, 'low');
addW(3990, 24400, 7800, 24400, 'low');
addW(7800, 23200, 7800, 24400, 'low');

addW(W_ENVELOPE - 7800, 23200, W_ENVELOPE - 7800, 24400, 'low');
addW(W_ENVELOPE - 7800, 24400, W_ENVELOPE - 3990, 24400, 'low');
addW(W_ENVELOPE - 3990, 24400, W_ENVELOPE - 3990, 25200, 'low');
addW(W_ENVELOPE - 3990, 25200, W_ENVELOPE - 200, 25200, 'low');
addW(W_ENVELOPE - 200, 23200, W_ENVELOPE - 200, 25200, 'low');

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

// 6. BEDROOM 1 (Image 2)
addTwin('bed', 'سرير نوم 1.5m', 2200, 8260, 1500, 2000, 0, '#c9d6df');
addTwin('nightstand', 'كومودينو أيسر', 1100, 7490, 450, 400, 0, '#e8dfd3');
addTwin('nightstand', 'كومودينو أيمن', 3300, 7490, 450, 400, 0, '#e8dfd3');
addTwin('wardrobe', 'دولاب ملابس', 2200, 10900, 1800, 600, 180, '#efe6d8');
addTwin('desk', 'مكتب دراسة', 3800, 9800, 1200, 600, 90, '#e2cfb4');

// 7. KITCHEN (Image 1 & 2)
addTwin('counter', 'كاونتر مطبخ رئيسي رخام', 2200, 11680, 2400, 600, 0, '#ffffff');
addTwin('stove', 'بوتاجاز مسطح', 3600, 11600, 750, 450, 0, '#2b2824');
addTwin('fridge', 'ثلاجة دولابي', 800, 14200, 910, 700, 270, '#c8cbd0');

// 8. GUEST BATH (Image 1)
addTwin('vanity', 'مغسلة ضيوف رخام', 1450, 14950, 900, 450, 0, '#ffffff');
addTwin('toilet', 'مرحاض ضيوف', 500, 15500, 400, 680, 270, '#ffffff');

// 9. GRAND RECEPTION (Image 1) - Expansive 7.71m x 7.15m luxury salon
addTwin('sofa', 'كنبة استقبال فاخرة 3 مقاعد', 700, 19625, 2400, 900, 270, '#b7c4b0');
addTwin('sofa', 'كنبة ثنائية متناسقة', 4000, 17200, 1800, 880, 0, '#c3cbd6');
addTwin('armchair', 'كرسي فوتيه مذهب', 4000, 22000, 850, 850, 180, '#d6b99a');
addTwin('rug', 'سجادة صالون استقبال كبرى', 2400, 19625, 3000, 2000, 270, '#d9cbb8');
addTwin('coffeetable', 'طاولة قهوة كالاتا رخام', 2400, 19625, 1300, 650, 270, '#e8dccb');
addTwin('tvstand', 'وحدة تلفزيون جدارية فاخرة', 7500, 19625, 2400, 400, 90, '#e2cfb4');

// 10. TERRACE (Image 1)
addTwin('plant', 'نبات زينة للتراس', 800, 24800, 500, 500, 0, '#9dbb8c');
addTwin('plant', 'نبات فيكس كبير', 7200, 23800, 700, 700, 0, '#9dbb8c');

const outputFurn = `// Default Furniture Dataset - 100% Calibrated from Authentic CAD Blueprint
export function defaultFurniture() {
  return ${JSON.stringify(defaultFurn, null, 2)};
}
`;

fs.writeFileSync('js/data/default-furniture.js', outputFurn, 'utf8');

console.log('Build completed successfully!');
console.log(`Rooms: ${ROOMS.length}, Walls: ${WALLS.length}, Doors: ${DOORS.length}, Furniture: ${defaultFurn.length}`);
