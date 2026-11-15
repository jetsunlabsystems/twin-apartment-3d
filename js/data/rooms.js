// Architectural Rooms Dataset - Calibrated authentic CAD room spaces & boundaries
export const BOUNDS = {"x":-800,"y":-800,"w":17400,"h":30600};

export const ROOMS = [
  {
    id: 'm_bed_l',
    name: 'جناح النوم الرئيسي',
    poly: [[200,200],[4200,200],[4200,5200],[200,5200]],
    mat: 'wood',
    wallMat: 'sage',
    at: [2200,2700]
  },
  {
    id: 'm_bath_l',
    name: 'حمام ماستر',
    poly: [[200,5320],[2140,5320],[2140,7120],[200,7120]],
    mat: 'marble',
    wallMat: 'mist',
    at: [1170,6220]
  },
  {
    id: 'm_closet_l',
    name: 'ملابس',
    poly: [[2260,5320],[4200,5320],[4200,7120],[2260,7120]],
    mat: 'wood',
    wallMat: 'greige',
    at: [3230,6220]
  },
  {
    id: 'bed2_l',
    name: 'غرفة نوم 2',
    poly: [[4320,200],[7800,200],[7800,4000],[4320,4000]],
    mat: 'wood',
    wallMat: 'desert',
    at: [6060,2100]
  },
  {
    id: 'laund_l',
    name: 'غرفة غسيل',
    poly: [[5800,4120],[7800,4120],[7800,6020],[5800,6020]],
    mat: 'tile800',
    wallMat: 'mist',
    at: [6800,5070]
  },
  {
    id: 'cbath_l',
    name: 'حمام عائلي',
    poly: [[5800,6140],[7800,6140],[7800,9540],[5800,9540]],
    mat: 'antislip',
    wallMat: 'mist',
    at: [6800,7840]
  },
  {
    id: 'bed1_l',
    name: 'غرفة نوم 1',
    poly: [[200,7240],[4490,7240],[4490,11240],[200,11240]],
    mat: 'wood',
    wallMat: 'greige',
    at: [2345,9240]
  },
  {
    id: 'living_l',
    name: 'غرفة المعيشة',
    poly: [[200,11360],[5840,11360],[5840,14960],[200,14960]],
    mat: 'wood',
    wallMat: 'alabaster',
    at: [3000,13160]
  },
  {
    id: 'kitchen_l',
    name: 'المطبخ',
    poly: [[200,15080],[4490,15080],[4490,18330],[200,18330]],
    mat: 'tile600',
    wallMat: 'mist',
    at: [2345,16705]
  },
  {
    id: 'gbath_l',
    name: 'حمام ضيوف',
    poly: [[200,18450],[4490,18450],[4490,19650],[200,19650]],
    mat: 'marble',
    wallMat: 'charcoal',
    at: [2345,19050]
  },
  {
    id: 'rec_l',
    name: 'صالون الاستقبال',
    poly: [[200,19650],[4490,19650],[4490,18600],[7800,18600],[7800,26920],[200,26920]],
    mat: 'marble',
    wallMat: 'alabaster',
    at: [4000,23345]
  },
  {
    id: 'terr_l',
    name: 'التراس',
    poly: [[200,26920],[3990,26920],[3990,28920],[200,28920]],
    mat: 'terrace',
    wallMat: 'alabaster',
    at: [2095,27920], counted: false
  },
  {
    id: 'm_bed_r',
    name: 'جناح النوم الرئيسي',
    poly: [[15600,5200],[11600,5200],[11600,200],[15600,200]],
    mat: 'wood',
    wallMat: 'sage',
    at: [13600,2700]
  },
  {
    id: 'm_bath_r',
    name: 'حمام ماستر',
    poly: [[15600,7120],[13660,7120],[13660,5320],[15600,5320]],
    mat: 'marble',
    wallMat: 'mist',
    at: [14630,6220]
  },
  {
    id: 'm_closet_r',
    name: 'ملابس',
    poly: [[13540,7120],[11600,7120],[11600,5320],[13540,5320]],
    mat: 'wood',
    wallMat: 'greige',
    at: [12570,6220]
  },
  {
    id: 'bed2_r',
    name: 'غرفة نوم 2',
    poly: [[11480,4000],[8000,4000],[8000,200],[11480,200]],
    mat: 'wood',
    wallMat: 'desert',
    at: [9740,2100]
  },
  {
    id: 'laund_r',
    name: 'غرفة غسيل',
    poly: [[10000,6020],[8000,6020],[8000,4120],[10000,4120]],
    mat: 'tile800',
    wallMat: 'mist',
    at: [9000,5070]
  },
  {
    id: 'cbath_r',
    name: 'حمام عائلي',
    poly: [[10000,9540],[8000,9540],[8000,6140],[10000,6140]],
    mat: 'antislip',
    wallMat: 'mist',
    at: [9000,7840]
  },
  {
    id: 'bed1_r',
    name: 'غرفة نوم 1',
    poly: [[15600,11240],[11310,11240],[11310,7240],[15600,7240]],
    mat: 'wood',
    wallMat: 'greige',
    at: [13455,9240]
  },
  {
    id: 'living_r',
    name: 'غرفة المعيشة',
    poly: [[15600,14960],[9960,14960],[9960,11360],[15600,11360]],
    mat: 'wood',
    wallMat: 'alabaster',
    at: [12800,13160]
  },
  {
    id: 'kitchen_r',
    name: 'المطبخ',
    poly: [[15600,18330],[11310,18330],[11310,15080],[15600,15080]],
    mat: 'tile600',
    wallMat: 'mist',
    at: [13455,16705]
  },
  {
    id: 'gbath_r',
    name: 'حمام ضيوف',
    poly: [[15600,19650],[11310,19650],[11310,18450],[15600,18450]],
    mat: 'marble',
    wallMat: 'charcoal',
    at: [13455,19050]
  },
  {
    id: 'rec_r',
    name: 'صالون الاستقبال',
    poly: [[8000,18600],[11310,18600],[11310,19650],[15600,19650],[15600,26920],[8000,26920]],
    mat: 'marble',
    wallMat: 'alabaster',
    at: [11800,23345]
  },
  {
    id: 'terr_r',
    name: 'التراس',
    poly: [[15600,28920],[11810,28920],[11810,26920],[15600,26920]],
    mat: 'terrace',
    wallMat: 'alabaster',
    at: [13705,27920], counted: false
  },
  {
    id: 'shaft_lightwell',
    name: 'منور رئيسي',
    poly: [[5840,9660],[9960,9660],[9960,13230],[5840,13230]],
    mat: 'antislip',
    wallMat: 'mist',
    at: [7900,11445], counted: false
  },
  {
    id: 'stair_core',
    name: 'الدرج والمصعد',
    poly: [[6040,13450],[9760,13450],[9760,17300],[6040,17300]],
    mat: 'tile800',
    wallMat: 'alabaster',
    at: [7900,15375], counted: false
  },
  {
    id: 'entry_lobby',
    name: 'مدخل الشقق الرئيسي',
    poly: [[6040,17300],[9760,17300],[9760,18600],[6040,18600]],
    mat: 'marble',
    wallMat: 'alabaster',
    at: [7900,17950], counted: false
  },
];

export const R = {};
ROOMS.forEach(r => { R[r.id] = r; });
