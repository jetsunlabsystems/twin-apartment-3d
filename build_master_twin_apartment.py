# -*- coding: utf-8 -*-
"""
Master Builder for Luxury Twin-Apartment 3D:
- High-end floors (Calacatta marble, French oak parquet, American walnut, slate tiles, non-slip stone, Venetian terrazzo)
- Architectural windows (bay windows, panoramic sliding patio glass, black aluminum mullions, stone sills)
- Millwork doors (door frames/architraves, walnut entrance doors with vertical pull bars, oak room doors with lever handles)
- Full 94-piece luxury interior design furniture package
- 2D CAD graphics for staircase, elevator, doors, and windows
- 3D U-shaped marble staircase and central glass panoramic elevator
- Google Font Tajawal Arabic localization with clean bilingual switcher
"""
import json
import os
import re

from generate_luxury_twin_arabic import build_refined_house

def generate_master_apartment():
    walls, wins, doors, slides, rooms, furniture = build_refined_house()

    base_dir = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d"
    src_path = os.path.join(base_dir, "index.upstream-demo.html")
    house_path = os.path.join(base_dir, "house-3d.html")
    index_path = os.path.join(base_dir, "index.html")

    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. HTML Header & Font (Tajawal)
    content = content.replace('<html lang="zh-CN">', '<html lang="ar" dir="rtl">')
    
    tajawal_head = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">"""
    
    content = re.sub(
        r'<meta charset="utf-8">\s*<meta name="viewport"[^>]+>',
        tajawal_head,
        content
    )
    
    content = content.replace(
        'font:13px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif',
        "font:14px/1.6 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    )
    content = content.replace(
        'button,input,select{font:inherit;color:inherit}',
        "button,input,select{font-family:'Tajawal',inherit;font-size:inherit;color:inherit}"
    )
    content = content.replace(
        'font-family="-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif"',
        'font-family="\'Tajawal\', -apple-system, sans-serif"'
    )

    # 2. UI Header & Action Buttons (Arabic)
    html_replacements = [
        ('>◧ 家具库<', '>◧ مكتبة الأثاث<'),
        ('>属性 ◨<', '>الخصائص ◨<'),
        ('data-en="◧ Library">◧ 家具库<', 'data-en="◧ Library">◧ مكتبة الأثاث<'),
        ('data-en="Properties ◨">属性 ◨<', 'data-en="Properties ◨">الخصائص ◨<'),
        ('三室两厅两卫 · 装修设计', 'عمارة سكنية فاخرة · شقتين متطابقتين'),
        ('data-en="3BR 2LR 2BA · Interior Design">三室两厅两卫 · 装修设计<', 'data-en="Luxury Twin Apartments · 3D Design">عمارة سكنية فاخرة · شقتين متطابقتين<'),
        ('原始户型 1:60 · 尺寸单位 mm', 'تصميم معماري وتأثيث داخلي 1:60 · الأبعاد بالمليمتر (mm)'),
        ('title="切换 2D / 3D (T)"', 'title="تبديل 2D / 3D (T)"'),
        ('>2D 平面<', '>مخطط 2D<'),
        ('>3D 场景<', '>مشهد 3D<'),
        ('title="选择 / 移动 (V)"', 'title="تحديد / تحريك (V)"'),
        ('>选择<', '>تحديد<'),
        ('title="测量 (M)"', 'title="قياس الأبعاد (M)"'),
        ('>测量<', '>قياس<'),
        ('title="拆改非承重墙 (X)"', 'title="تعديل الجدران (X)"'),
        ('>拆改墙体<', '>تعديل الجدران<'),
        ('title="缩小"', 'title="تصغير"'),
        ('title="放大"', 'title="تكبير"'),
        ('title="适应窗口 (F)"', 'title="ملاءمة الشاشة (F)"'),
        ('>适应<', '>ملاءمة<'),
        ('title="按 1:60 显示（与原图同比例）"', 'title="عرض بمقياس 1:60 (مطابق للمخطط الأصلي)"'),
        ('title="按 1:100 显示"', 'title="عرض بمقياس 1:100"'),
        ('>鸟瞰<', '>منظور علوي<'),
        ('>漫游<', '>جولة 3D<'),
        ('>斜视<', '>منظور مائل<'),
        ('>俯视<', '>مسقط رأسي<'),
        ('title="撤销 (Ctrl+Z)"', 'title="تراجع (Ctrl+Z)"'),
        ('>撤销<', '>تراجع<'),
        ('title="重做 (Ctrl+Shift+Z)"', 'title="إعادة (Ctrl+Shift+Z)"'),
        ('>重做<', '>إعادة<'),
        ('title="清空所有家具家电（可撤销）"', 'title="إفراغ جميع الأثاث (يمكن التراجع)"'),
        ('>清空布置<', '>إفراغ التأثيث<'),
        ('>尺寸<', '>الأبعاد<'),
        ('>房间<', '>الغرف<'),
        ('>家具<', '>الأثاث<'),
        ('>网格<', '>الشبكة<'),
        ('>承重墙<', '>جدران حاملة<'),
        ('title="拖动家具时贴墙吸附"', 'title="محاذاة ومغناطيسية للجدران أثناء السحب"'),
        ('>贴墙吸附<', '>محاذاة للجدار<'),
        ('>全高墙<', '>جدران كاملة<'),
        ('>低矮墙<', '>جدران منخفضة<'),
        ('>家具<', '>الأثاث<'),
        ('>标签<', '>تسميات الغرف<'),
        ('>夜景<', '>إضاءة ليلية<'),
        ('title="白昼太阳高度 / 方位角"', 'title="زاوية وارتفاع أشعة الشمس"'),
        ('title="键盘与手势快捷键帮助 (?)"', 'title="دليل اختصارات لوحة المفاتيح واللمس (?)"'),
        ('title="全屏显示"', 'title="ملء الشاشة"'),
        ('title="在手机或平板上用 Safari 打开并添加到主屏幕，即可全屏沉浸使用"', 'title="يمكن فتحه وإضافته للشاشة الرئيسية للاستمتاع بتجربة ملء الشاشة"'),
        ('title="文件操作"', 'title="ملف"'),
        ('>文件 ▾<', '>ملف ▾<'),
        ('>保存方案 (JSON)<', '>حفظ التصميم (JSON)<'),
        ('>打开方案 (JSON)...<', '>فتح تصميم (JSON)...<'),
        ('>导出户型图 (PNG)<', '>تصدير المخطط (PNG)<'),
        ('>导出 3D 效果图 (PNG)<', '>تصدير صورة ثلاثية الأبعاد (PNG)<'),
        ('>重置为默认户型布置<', '>استعادة المخطط الأصلي الافتراضي<'),
        ('房间 · 点击定位', 'قائمة الغرف · اضغط للانتقال'),
        ('>全部展开<', '>توسيع الكل<'),
        ('>全部折叠<', '>طي الكل<'),
        ('search-kw" placeholder="搜索家具 / 拼音..."', 'search-kw" placeholder="بحث عن الأثاث..."'),
        ('data-en="Bed">卧室<', 'data-en="Bed">غرف النوم<'),
        ('data-en="Living">客餐厅<', 'data-en="Living">الصالون والمعيشة<'),
        ('data-en="Kitchen">厨卫<', 'data-en="Kitchen">المطبخ وتناول الطعام<'),
        ('data-en="Study">书房儿童<', 'data-en="Study">المكتب والترفيه<'),
        ('data-en="Appliances">家电<', 'data-en="Appliances">الأجهزة المنزلية<'),
        ('data-en="Other">其他<', 'data-en="Other">الحمامات والديكور<'),
        ('点击平面图中的家具、房间或墙体，在这里查看与修改。', 'اضغط على أي قطعة أثاث أو غرفة أو جدار لتعديل الأبعاد والألوان والخامات.'),
        ('>剖切墙<', '>جدران مقطوعة<'),
        ('>房间名<', '>تسميات الغرف<'),
        ('>日照<', '>أشعة الشمس<'),
        ('title="简体中文">简<', 'title="العربية">عربي<'),
        ('title="繁體中文">繁<', 'title="English">EN<'),
        ('data-lang="zht"', 'data-lang="en"'),
        ('>导出图片<', '>تصدير صورة<'),
        ('>导出方案 JSON<', '>تصدير JSON<'),
        ('>导入方案<', '>استيراد تصميم<'),
        ('>重置为默认方案<', '>استعادة الافتراضي<'),
        ('房间 · 点击飞到该房间', 'قائمة الغرف · اضغط للطيران إليها'),
        ('>漫游模式<', '>وضع الجولة الافتراضية<'),
        ('>退出漫游<', '>الخروج من الجولة<'),
        ('当前比例', 'المقياس الحالي'),
    ]

    for zh, ar in html_replacements:
        content = content.replace(zh, ar)

    # 3. Clean CSS for `.rlabel` (Non-overlapping pill badges)
    old_rlabel_css = """.rlabel{font-size:12px;font-weight:600;color:#2b2824;background:rgba(255,253,249,.9);border:1px solid var(--line);
  border-radius:12px;padding:2px 9px;white-space:nowrap;pointer-events:none}
.rlabel small{font-weight:400;color:var(--muted);margin-left:4px}"""

    new_rlabel_css = """.rlabel{font-family:'Tajawal',sans-serif;font-size:11.5px;font-weight:700;color:#0f172a;background:rgba(255,255,255,0.92);
  border:1px solid rgba(0,0,0,0.12);border-radius:18px;padding:2px 9px;white-space:nowrap;pointer-events:none;
  box-shadow:0 3px 8px rgba(0,0,0,0.10);backdrop-filter:blur(4px);display:flex;align-items:center;gap:5px}
.rlabel small{font-weight:600;color:#b5653a;background:rgba(181,101,58,0.12);padding:1px 5px;border-radius:8px;font-size:10px}"""
    content = content.replace(old_rlabel_css, new_rlabel_css)

    # 4. Replace Language Engine block strictly
    idx_lang_start = content.find("/* ======================= 多语言")
    idx_lang_end_marker = "b.setAttribute('aria-pressed', on); });\n}"
    idx_lang_end = content.find(idx_lang_end_marker) + len(idx_lang_end_marker)

    clean_lang_engine = """/* ======================= 多语言 / Localization (Arabic Tajawal Default) ======================= */
const LANG_MAP = {
  zh: 'العربية',
  en: 'English'
};
let curLang = localStorage.getItem('app_lang') || 'zh';

function tr(arText, enText){
  return curLang === 'en' ? (enText || arText) : arText;
}

function nm(o){
  if (!o) return '';
  if (typeof o === 'string') return o;
  return curLang === 'en' ? (o.en || o.zh || '') : (o.zh || o.en || '');
}

function setLang(l){
  curLang = (l === 'zht' || l === 'en') ? 'en' : 'zh';
  localStorage.setItem('app_lang', curLang);
  document.documentElement.lang = curLang === 'zh' ? 'ar' : 'en';
  document.documentElement.dir = curLang === 'zh' ? 'rtl' : 'ltr';
  applyStaticLang();
  renderProps();
  renderPlan();
  if (typeof buildFurn === 'function') buildFurn();
  if (typeof buildLabels === 'function') buildLabels();
  if (typeof updateFlyRoomList === 'function') updateFlyRoomList();
  renderLib();
  updateHelpTable();
  updateHints();
}

function applyStaticLang(){
  document.querySelectorAll('[data-en]').forEach(el => {
    if (!el.dataset.zh) el.dataset.zh = el.textContent;
    el.textContent = curLang === 'en' ? el.dataset.en : el.dataset.zh;
  });
  document.querySelectorAll('#langSel .btn').forEach(b => {
    const l = b.dataset.lang;
    const on = (curLang === 'zh' && l === 'zh') || (curLang === 'en' && (l === 'en' || l === 'zht'));
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
}"""

    content = content[:idx_lang_start] + clean_lang_engine + content[idx_lang_end:]

    # 5. Replace WALLS, WINS, DOORS, SLIDES, ROOMS block (from 'const WALLS =' to 'const MATS =')
    pos_walls_start = content.find('const WALLS =')
    pos_mats_start = content.find('const MATS =')

    model_data_block = f"""const WALLS = {json.dumps(walls, indent=2, ensure_ascii=False)};
const WINS = {json.dumps(wins, indent=2, ensure_ascii=False)};
const DOORS = {json.dumps(doors, indent=2, ensure_ascii=False)};
const SLIDES = {json.dumps(slides, indent=2, ensure_ascii=False)};
const R = (x0,y0,x1,y1) => [[x0,y0],[x1,y0],[x1,y1],[x0,y1]];
const ROOMS = {json.dumps(rooms, indent=2, ensure_ascii=False)};
"""
    content = content[:pos_walls_start] + model_data_block + content[pos_mats_start:]

    # 6. Replace MATS dictionary
    pos_mats_start = content.find('const MATS =')
    pos_lib_start = content.find('const LIB =')

    new_mats = """const MATS = {
  marble:  {name:{zh:'رخام إيطالي كالاتا مصقول', en:'Polished Italian Calacatta Marble'}, price:680, sw:'#f6f3ee'},
  wood:    {name:{zh:'باركيه خشب بلوط فرنسي فاخر', en:'French Oak Natural Parquet'}, price:380, sw:'#c9985d'},
  walnut:  {name:{zh:'باركيه خشب جوز ملكي داكن', en:'Dark American Walnut Flooring'}, price:420, sw:'#724c30'},
  tile800: {name:{zh:'بورسلان بيج دافئ كبير 800×800', en:'Warm Ivory Porcelain Tiles 800x800'}, price:240, sw:'#ebe5d9'},
  tile600: {name:{zh:'بورسلان رمادي حجري للمطبخ 600×600', en:'Modern Slate Kitchen Tiles 600x600'}, price:190, sw:'#596168'},
  antislip:{name:{zh:'حجر مانع للانزلاق للحمامات', en:'Textured Non-Slip Bathroom Stone'}, price:170, sw:'#3d444b'},
  terrazzo:{name:{zh:'تيرازو فينيسي مودرن للتراس', en:'Venetian Terrazzo Balcony Tiles'}, price:290, sw:'#e4ddcf'},
  carpet:  {name:{zh:'سجاد صوف فاخر', en:'Plush Wool Carpet'}, price:220, sw:'#b8b0c4'},
};
"""
    content = content[:pos_mats_start] + new_mats + content[pos_lib_start:]

    # 7. Furniture Library (LIB) - Arabic Translated
    pos_lib_start = content.find('const LIB =')
    pos_def_furn_start = content.find('function defaultFurniture()')

    new_lib = """const LIB = [
  {cat:'غرف النوم', items:[
    ['bed','سرير كينج 1.8m',1800,2000,'#c9d6df'],['bed','سرير كوين 1.5m',1500,2000,'#d8c7dc'],['bed','سرير مفرد',1200,2000,'#e8d5b5'],
    ['crib','سرير أطفال',1250,700,'#efe3d0'],['nightstand','كومودينو',450,400,'#e8dccb'],['wardrobe','دولاب ملابس كبير',2000,600,'#efe6d8'],
    ['wardrobe','خزانة ملابس متوسطة',1200,550,'#efe6d8'],['dresser','تسريحة ومرآة',1000,450,'#efe6d8'],['desk','مكتب دراسة',1200,600,'#e2cfb4'],
    ['chair','كرسي مكتب',450,480,'#cfc6b8'],['bookshelf','مكتبة كتب',800,300,'#e2cfb4'],['baycushion','جلسة شباك بانوراما',520,1800,'#e7dccd']]},
  {cat:'الصالون والمعيشة', items:[
    ['sofa','كنبة 3 مقاعد فاخرة',2400,900,'#b7c4b0'],['sofa','كنبة ثنائية',1700,880,'#c3cbd6'],['cornersofa','كنبة زاوية عائلية مودرن',2800,1700,'#b7c4b0'],
    ['armchair','كرسي فوتيه مذهب',850,850,'#d6b99a'],['beanbag','بين باج استرخاء',800,800,'#e0b98f'],['coffeetable','طاولة رخام كالاتا',1300,650,'#e8dccb'],
    ['sidetable','طاولة جانبية',500,500,'#d9c3a3'],['tvstand','وحدة تلفزيون جدارية',2400,400,'#e2cfb4'],['rug','سجادة صالون مودرن',2400,1700,'#d9cbb8'],
    ['shoecab','خزانة أحذية',1000,350,'#efe6d8'],['shoecab','كونسول مدخل',1400,380,'#e6dccc'],['floorlamp','مصباح أرضي مودرن',450,450,'#3d3a34'],
    ['plant','نبات زينة داخلي',500,500,'#a9c39b'],['plant','نبات فيكس كبير',700,700,'#9dbb8c']]},
  {cat:'المطبخ وتناول الطعام', items:[
    ['table','طاولة طعام 4 كراسي',1400,800,'#e2cfb4'],['table','طاولة طعام 6 كراسي',1800,900,'#d8c2a2'],['roundtable','طاولة طعام دائرية',1000,1000,'#e8d5be'],
    ['diningchair','كرسي طعام',450,450,'#cfc2af'],['barstool','كرسي بار كاونتر',400,400,'#3d3a34'],['counter','كاونتر مطبخ رخام',1600,600,'#ffffff'],
    ['ksink','حوض غسيل ستانلس',800,450,'#3d3a34'],['stove','بوتاجاز غاز مسطح',750,450,'#2b2824'],['fridge','ثلاجة دولابي',910,700,'#c8cbd0'],
    ['island','جزيرة مطبخ رخام',1600,800,'#efe6d8']]},
  {cat:'المكتب والترفيه', items:[
    ['execdesk','مكتب مدير فاخر',1600,800,'#8b6848'],['officechair','كرسي مكتب تنفيذي',650,650,'#2b2b2d'],['bookshelf','مكتبة كتب جدارية',1200,350,'#e2cfb4'],
    ['tv','شاشة تلفزيون 65 بوصة',1450,80,'#111111'],['piano','بيانو كلاسيكي أسود',1500,600,'#1a1a1a'],['treadmill','مشاية رياضية كهربائية',1700,750,'#3d4044']]},
  {cat:'الحمامات والديكور', items:[
    ['toilet','مرحاض معلق مودرن',400,680,'#ffffff'],['vanity','مغسلة ديكور رخام',900,520,'#ffffff'],['bathtub','حوض استحمام بانيو',1500,750,'#ffffff'],
    ['shower','شاور زجاجي فاخر',900,900,'#cfe6ef'],['washer','غسالة ملابس أوتوماتيك',600,600,'#e5e7ea']]},
];
"""
    content = content[:pos_lib_start] + new_lib + content[pos_def_furn_start:]

    # 8. Initial Default Furniture (Full 94-piece interior package)
    pos_def_furn_start = content.find('function defaultFurniture()')
    pos_def_state_start = content.find('function defaultState()')

    furn_items_js = []
    for f_idx, item in enumerate(furniture):
        ftype, fname, fcx, fcy, fw, fd, frot, fcol = item
        entry = {
            "id": f"f_{f_idx+1}",
            "type": ftype,
            "name": {"zh": fname, "en": fname},
            "cx": fcx,
            "cy": fcy,
            "w": fw,
            "d": fd,
            "rot": frot
        }
        if fcol:
            entry["color"] = fcol
        furn_items_js.append(entry)

    new_default_furniture = f"""function defaultFurniture(){{
  return {json.dumps(furn_items_js, indent=4, ensure_ascii=False)};
}}
"""
    content = content[:pos_def_furn_start] + new_default_furniture + content[pos_def_state_start:]

    # 9. Update BOUNDS and Storage Key
    content = content.replace("const BOUNDS = {x:-1850, y:-1750, w:15600, h:14100};", "const BOUNDS = {x:-1000, y:-1000, w:17800, h:27700};")
    content = content.replace("const STORE = 'floorplan-3d-v4';", "const STORE = 'twin-apartment-luxury-v3';")
    content = content.replace("const STORE = 'twin-apartment-house-3d-v5';", "const STORE = 'twin-apartment-luxury-v3';")

    # 10. 2D CAD Drawings in `renderOpenings` (Windows, Doors, Stairs, Elevator)
    pos_openings_start = content.find('function renderOpenings(){')
    pos_labels_start = content.find('function renderLabels(){')

    new_render_openings = """function renderOpenings(){
  const WS = 'stroke="#4f7394" stroke-width="1.2" vector-effect="non-scaling-stroke"';
  let s = '';
  WINS.forEach(([x0,y0,x1,y1]) => {
    const w = x1-x0, h = y1-y0;
    s += `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" fill="#f0f7fa" ${WS}/>`;
    if (w >= h) [1/3,2/3].forEach(t => s += `<line x1="${x0}" y1="${y0+h*t}" x2="${x1}" y2="${y0+h*t}" ${WS}/>`);
    else [1/3,2/3].forEach(t => s += `<line x1="${x0+w*t}" y1="${y0}" x2="${x0+w*t}" y2="${y1}" ${WS}/>`);
  });
  const DS = 'stroke="#2d3748" stroke-width="1.2" vector-effect="non-scaling-stroke"';
  DOORS.forEach(d => {
    const [hx,hy] = d.h, L = d.len, T = 40;
    const ox = hx + d.o[0]*L, oy = hy + d.o[1]*L, cx = hx + d.c[0]*L, cy = hy + d.c[1]*L;
    const sweep = d.o[0]*d.c[1] - d.o[1]*d.c[0] > 0 ? 1 : 0;
    const col = d.entry ? '#b5653a' : '#4a5568';
    s += `<polygon points="${hx},${hy} ${ox},${oy} ${ox+d.c[0]*T},${oy+d.c[1]*T} ${hx+d.c[0]*T},${hy+d.c[1]*T}" fill="#fff" stroke="${col}" stroke-width="${d.entry?2.2:1.2}" vector-effect="non-scaling-stroke"/>`;
    s += `<path d="M${ox} ${oy}A${L} ${L} 0 0 ${sweep} ${cx} ${cy}" fill="none" ${DS} stroke-dasharray="6 4" opacity=".75"/>`;
  });
  SLIDES.forEach(({rect:[x0,y0,x1,y1],v}) => {
    if (v){ const L = y1-y0, m = (x0+x1)/2; s += `<rect x="${m-45}" y="${y0}" width="40" height="${L*.55}" fill="#fff" ${DS}/><rect x="${m+5}" y="${y1-L*.55}" width="40" height="${L*.55}" fill="#fff" ${DS}/>`; }
    else { const L = x1-x0, m = (y0+y1)/2; s += `<rect x="${x0}" y="${m-45}" width="${L*.55}" height="40" fill="#fff" ${DS}/><rect x="${x1-L*.55}" y="${m+5}" width="${L*.55}" height="40" fill="#fff" ${DS}/>`; }
  });

  // 2D Elevator Shaft & Cabin
  s += `<rect x="7140" y="11900" width="1520" height="1500" fill="#f8fafc" stroke="#1e293b" stroke-width="2" vector-effect="non-scaling-stroke"/>`;
  s += `<line x1="7140" y1="11900" x2="8660" y2="13400" stroke="#94a3b8" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
  s += `<line x1="8660" y1="11900" x2="7140" y2="13400" stroke="#94a3b8" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
  s += `<rect x="7240" y="12000" width="1320" height="1300" fill="none" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="8 4" vector-effect="non-scaling-stroke"/>`;
  s += `<text x="7900" y="12720" font-family="'Tajawal', sans-serif" font-size="190" font-weight="700" fill="#0284c7" text-anchor="middle">مصعد ELEVATOR</text>`;

  // 2D Staircase Treads & Climb Arrows
  for (let i = 0; i <= 8; i++) {
    const y = 14650 - 400 - i * 300;
    s += `<line x1="6040" y1="${y}" x2="7140" y2="${y}" stroke="#64748b" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
    s += `<line x1="8660" y1="${y}" x2="9760" y2="${y}" stroke="#64748b" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
  }
  // Mid Landing box
  s += `<rect x="6040" y="11350" width="3720" height="500" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
  s += `<text x="7900" y="11650" font-family="'Tajawal', sans-serif" font-size="160" font-weight="600" fill="#64748b" text-anchor="middle">استراحة وسطية MID-LANDING</text>`;

  // Climb arrows
  s += `<line x1="6590" y1="14550" x2="6590" y2="12000" stroke="#0f172a" stroke-width="2.5" vector-effect="non-scaling-stroke"/>`;
  s += `<polygon points="6590,11880 6540,12020 6640,12020" fill="#0f172a"/>`;
  s += `<circle cx="6590" cy="14550" r="45" fill="#0f172a"/>`;
  s += `<text x="6590" y="13350" font-family="'Tajawal', sans-serif" font-size="160" font-weight="700" fill="#0f172a" text-anchor="middle">صعود UP</text>`;

  $('#gOpenings').innerHTML = s;
}
"""
    content = content[:pos_openings_start] + new_render_openings + content[pos_labels_start:]

    # 11. Floor Textures Procedural Generation (TEX & floorMat)
    pos_tex_start = content.find("const TEX = {")
    pos_geom_start = content.find("/* ======================= 几何小工具")

    new_tex_block = """const TEX = {
  marble:  {sx:1.8, sy:1.8, base:'#faf8f5', grout:'#e0d9cc', rough:.10},
  wood:    {sx:1.8, sy:.38, base:'#c9965d', rough:.38},
  walnut:  {sx:1.8, sy:.38, base:'#724c30', rough:.35},
  tile800: {sx:1.2, sy:1.2, base:'#e9e3d8', grout:'#bfb5a3', rough:.20},
  tile600: {sx:.9, sy:.9, base:'#596168', grout:'#3b4147', rough:.28},
  antislip:{sx:.6, sy:.6, base:'#3d444b', grout:'#23282c', rough:.75},
  terrazzo:{sx:.8, sy:.8, base:'#e4ddcf', rough:.30},
  carpet:  {sx:.4, sy:.4, base:'#c4bdcd', rough:1},
};
const floorMats = {};
function floorMat(kind){
  if (floorMats[kind]) return floorMats[kind];
  const s = TEX[kind] || TEX.tile800, R = rng(kind.length*977 + 13), cv = document.createElement('canvas');
  const wood = kind === 'wood' || kind === 'walnut';
  cv.width = wood ? 1024 : 1024; cv.height = wood ? 256 : 1024;
  const g = cv.getContext('2d'), W = cv.width, Hh = cv.height;
  g.fillStyle = s.base; g.fillRect(0, 0, W, Hh);
  
  if (wood){
    const rowH = Hh/2, joints = [[W*2/3], [W/3]];
    for (let r = 0; r < 2; r++){
      let x0 = 0;
      [...joints[r], W].forEach(x1 => {
        g.fillStyle = rgbK(s.base, .92 + R()*.16); g.fillRect(x0, r*rowH, x1-x0, rowH);
        g.strokeStyle = rgbK(s.base, .78); g.globalAlpha = .35; g.lineWidth = 1.4;
        for (let k = 0; k < 8; k++){
          const y = r*rowH + 6 + R()*(rowH-12); g.beginPath(); g.moveTo(x0, y);
          for (let x = x0; x <= x1; x += 35) g.lineTo(x, y + Math.sin(x*.025 + k)*2.8); g.stroke();
        }
        g.globalAlpha = 1;
        g.fillStyle = rgbK(s.base, .55); g.fillRect(x1-2, r*rowH, 4, rowH); x0 = x1;
      });
      g.fillStyle = rgbK(s.base, .55); g.fillRect(0, r*rowH, W, 3.5);
    }
  } else if (kind === 'marble'){
    for (let c = 0; c < 15; c++){
      const grad = g.createRadialGradient(R()*W, R()*Hh, 30, R()*W, R()*Hh, 240);
      grad.addColorStop(0, 'rgba(238,230,220,0.45)');
      grad.addColorStop(1, 'rgba(250,248,245,0)');
      g.fillStyle = grad; g.fillRect(0, 0, W, Hh);
    }
    const veinColors = ['rgba(140,130,115,0.45)', 'rgba(185,155,115,0.4)', 'rgba(115,110,100,0.35)'];
    for (let k = 0; k < 9; k++){
      g.strokeStyle = veinColors[k % veinColors.length];
      g.lineWidth = 1.2 + R()*3.5;
      g.beginPath();
      let x = R()*W, y = 0;
      g.moveTo(x, y);
      for (let s = 0; s < 4; s++){
        const nx = x + (R() - 0.3)*W*0.6, ny = y + Hh*0.25;
        g.bezierCurveTo(x + (R()-0.5)*120, y + 60, nx + (R()-0.5)*120, ny - 60, nx, ny);
        if (R() > 0.45){
          g.stroke(); g.beginPath(); g.moveTo(nx, ny); g.lineWidth *= 0.6;
          g.lineTo(nx + (R()-0.5)*180, ny + (R()-0.3)*120); g.stroke();
          g.beginPath(); g.moveTo(nx, ny);
        }
        x = nx; y = ny;
      }
      g.stroke();
    }
    g.fillStyle = s.grout; g.fillRect(0, 0, W, 4); g.fillRect(0, 0, 4, Hh);
    g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillRect(4, 4, W-4, 2); g.fillRect(4, 4, 2, Hh-4);
  } else if (kind === 'terrazzo'){
    const cs = ['#b9a58c','#8fa3a0','#c9b7a2','#a88f76','#7e8a86','#ffffff'];
    for (let k = 0; k < 280; k++){
      g.fillStyle = cs[k%cs.length]; g.beginPath(); g.arc(R()*W, R()*Hh, 2 + R()*8, 0, 7); g.fill();
    }
    if (s.grout){ g.fillStyle = s.grout; g.fillRect(0, 0, W, 4); g.fillRect(0, 0, 4, Hh); }
  } else {
    for (let k = 0; k < 1800; k++){ g.fillStyle = `rgba(0,0,0,${R()*.04})`; g.fillRect(R()*W, R()*Hh, 2, 2); }
    if (s.grout){
      g.fillStyle = s.grout; g.fillRect(0, 0, W, 5); g.fillRect(0, 0, 5, Hh);
      g.fillStyle = 'rgba(255,255,255,0.3)'; g.fillRect(5, 5, W-5, 2); g.fillRect(5, 5, 2, Hh-5);
    }
  }
  const t = new THREE.CanvasTexture(cv);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1/s.sx, 1/s.sy);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return floorMats[kind] = new THREE.MeshStandardMaterial({map:t, roughness:s.rough, metalness:kind==='marble'?0.05:0});
}
"""
    content = content[:pos_tex_start] + new_tex_block + content[pos_geom_start:]

    # 12. 3D Architectural Geometry in `buildArch`
    pos_build_arch_start = content.find("function buildArch(){")
    pos_build_furn_start = content.find("function buildFurn(){")

    new_build_arch = """function buildArch(){
  clearGroup(archFloor); clearGroup(archUp); lampG.clear(); doors.length = 0; colliders = [];
  const top = opt.cut;
  
  // 1. Room Floors & Ceilings
  ROOMS.forEach(r => {
    const m = floorMat(state.rooms[r.id].mat), bay = r.counted === false;
    const geo = bay ? new THREE.ExtrudeGeometry(shapeOf(r.poly), {depth:.45, bevelEnabled:false}) : new THREE.ShapeGeometry(shapeOf(r.poly));
    geo.rotateX(-Math.PI/2);
    const fl = new THREE.Mesh(geo, bay ? [m, mat('#e9e4da')] : m);
    fl.receiveShadow = true; fl.userData.room = r.id;
    if (bay){ fl.castShadow = true; archUp.add(fl); } else archFloor.add(fl);
    const cg = new THREE.ShapeGeometry(shapeOf(r.poly, true)); cg.rotateX(Math.PI/2);
    const ceil = new THREE.Mesh(cg, mat('#fbfaf7', {roughness:1})); ceil.position.y = H; ceil.visible = top >= H; archUp.add(ceil);
    if (r.at){
      const lamp = new THREE.Mesh(new THREE.CylinderGeometry(.22, .22, .02, 32), new THREE.MeshStandardMaterial({color:'#fff', emissive:'#fff2d6', emissiveIntensity:.3}));
      lamp.position.set(wx(r.at[0]), H - .012, wz(r.at[1])); lamp.visible = top >= H; lampG.add(lamp);
      const pl = new THREE.PointLight(0xffd9a8, 0, 7, 1.6); pl.position.set(wx(r.at[0]), H - .25, wz(r.at[1])); lampG.add(pl);
    }
  });

  // Threshold floor strips
  [...DOORS, ...SLIDES].forEach(d => {
    const [x0, y0, x1, y1] = d.rect;
    const s = box(M(x1-x0), .012, M(y1-y0), mat('#c8bfb0', {roughness:.3}), wx((x0+x1)/2), 0, wz((y0+y1)/2));
    s.castShadow = false; archFloor.add(s);
  });

  // 2. Walls & Balustrades
  WALLS.forEach((w, i) => {
    if (state.demolished.includes('w'+i)) return;
    if (w[4] === 'low'){
      // Modern Terrace Balustrade: 0.25m low curb + glass balustrade with dark bronze / stainless handrail
      const curbH = Math.min(0.25, top);
      wallBox(w, 0, curbH);
      if (top > 0.25){
        const railTop = Math.min(1.05, top);
        const [x0, y0, x1, y1] = w, hz = (x1-x0) >= (y1-y0), L = M(hz ? x1-x0 : y1-y0), cx = wx((x0+x1)/2), cz = wz((y0+y1)/2);
        const bGlass = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : 0.015, railTop - 0.25, hz ? 0.015 : L), glassMat);
        bGlass.position.set(cx, 0.25 + (railTop - 0.25)/2, cz);
        archUp.add(bGlass);
        // Architectural top handrail
        const hRail = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : 0.06, 0.045, hz ? 0.06 : L), metal('#1a1a1a'));
        hRail.position.set(cx, railTop, cz);
        archUp.add(hRail);
        // Vertical balustrade posts
        const pn = Math.max(1, Math.round(L / 1.2));
        for (let p = 0; p <= pn; p++){
          const pt = -L/2 + p * L/pn;
          const post = new THREE.Mesh(new THREE.BoxGeometry(hz ? 0.04 : 0.05, railTop - 0.25, hz ? 0.05 : 0.04), metal('#1a1a1a'));
          post.position.set(cx + (hz ? pt : 0), 0.25 + (railTop - 0.25)/2, cz + (hz ? 0 : pt));
          archUp.add(post);
        }
      }
    } else {
      wallBox(w, 0, top);
    }
    colliders.push([wx(w[0]), wz(w[1]), wx(w[2]), wz(w[3])]);
  });

  // Wall lintels above door openings
  [...DOORS.map(d => [d.rect, 2.1]), ...SLIDES.map(s => [s.rect, s.v ? 2.4 : 2.1])]
    .forEach(([r, h]) => { if (top > h) wallBox(r, h, top); });

  // 3. Architectural Windows
  WINS.forEach((r, i) => {
    const sill = r[4] !== undefined ? r[4] : (i === 0 ? 1.4 : i >= 6 ? .45 : .9);
    const head = r[5] !== undefined ? r[5] : 2.4;
    wallBox(r, 0, Math.min(sill, top));
    if (top > head) wallBox(r, head, top);
    colliders.push([wx(r[0]), wz(r[1]), wx(r[2]), wz(r[3])]);
    const gTop = Math.min(head, top);
    if (gTop <= sill) return;
    const [x0, y0, x1, y1] = r, hz = (x1-x0) >= (y1-y0), L = M(hz ? x1-x0 : y1-y0), gh = gTop - sill, cx = wx((x0+x1)/2), cz = wz((y0+y1)/2);
    
    // Glass pane
    const pane = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : .015, gh, hz ? .015 : L), glassMat);
    pane.position.set(cx, sill + gh/2, cz);
    archUp.add(pane);

    // Deep window sill ledge (warm stone/aluminum trim)
    const sillMesh = new THREE.Mesh(new THREE.BoxGeometry(hz ? L + 0.06 : 0.32, 0.035, hz ? 0.32 : L + 0.06), mat('#dcd8ce', {roughness:.3}));
    sillMesh.position.set(cx, sill - 0.015, cz);
    archUp.add(sillMesh);

    // Black architectural aluminum mullions
    const n = Math.max(1, Math.round(L/.85));
    for (let k = 0; k <= n; k++){
      const t = -L/2 + k*L/n;
      const mu = new THREE.Mesh(new THREE.BoxGeometry(hz ? .045 : .075, gh, hz ? .075 : .045), frameMat);
      mu.position.set(cx + (hz ? t : 0), sill + gh/2, cz + (hz ? 0 : t));
      mu.castShadow = true;
      archUp.add(mu);
    }
    // Horizontal transom rails
    [sill + .02, gTop - .02].forEach(y => {
      const tr = new THREE.Mesh(new THREE.BoxGeometry(hz ? L : .075, .045, hz ? .075 : L), frameMat);
      tr.position.set(cx, y, cz);
      archUp.add(tr);
    });
  });

  // 4. Millwork Doors (Frames, Walnut Entrance Doors, Oak Interior Doors)
  DOORS.forEach(d => {
    const L = M(d.len), dh = Math.min(2.05, top);
    const cAng = Math.atan2(-d.c[1], d.c[0]);

    // Architectural Door Frame (Jambs + Header)
    const frameCol = d.entry ? '#2a1a10' : '#4a382c';
    const frameM = mat(frameCol, {roughness:.4});
    const fG = new THREE.Group();
    fG.position.set(wx(d.h[0]), 0, wz(d.h[1]));
    fG.rotation.y = cAng;
    fG.add(box(0.05, Math.min(2.12, top), 0.16, frameM, 0.025, 0, 0));
    fG.add(box(0.05, Math.min(2.12, top), 0.16, frameM, L - 0.025, 0, 0));
    if (top > 2.05) fG.add(box(L, 0.06, 0.16, frameM, L/2, Math.min(2.05, top), 0));
    archUp.add(fG);

    // Pivotable Door Leaf
    const pivot = new THREE.Group();
    pivot.position.set(wx(d.h[0]), 0, wz(d.h[1]));
    const doorWood = mat(d.entry ? '#342114' : '#8a6240', {roughness: 0.38});
    const leaf = box(L - 0.02, dh, 0.045, doorWood, L/2);

    if (d.entry){
      for (let k = 0; k < 4; k++){
        leaf.add(box(L * 0.72, 0.012, 0.048, mat('#151210', {roughness:.2, metalness:.8}), L/2, 0.4 + k * 0.42, 0));
      }
      const handleBar = cyl(0.014, 0.014, 0.65, metal('#e2e8f0'), L - 0.12, 0.7, 0.045);
      const post1 = box(0.02, 0.02, 0.04, metal(), L - 0.12, 0.75, 0.025);
      const post2 = box(0.02, 0.02, 0.04, metal(), L - 0.12, 1.25, 0.025);
      leaf.add(handleBar, post1, post2);
    } else {
      for (let k = 0; k < 3; k++){
        leaf.add(box(L * 0.78, 0.01, 0.047, mat('#6b4c30', {roughness:.5}), L/2, 0.5 + k * 0.5, 0));
      }
      const escPlate = box(0.045, 0.15, 0.05, metal(), L - 0.08, 0.95, 0);
      const lever = box(0.12, 0.018, 0.02, metal(), L - 0.04, 0.98, 0.035);
      leaf.add(escPlate, lever);
    }

    pivot.add(leaf);
    const ang = v => Math.atan2(-v[1], v[0]), door = {pivot, a0:ang(d.c), a1:ang(d.o), open:true};
    if (door.a1 - door.a0 > Math.PI) door.a1 -= Math.PI*2; if (door.a0 - door.a1 > Math.PI) door.a1 += Math.PI*2;
    door.cur = door.a1; pivot.rotation.y = door.cur; leaf.userData.door = door;
    doors.push(door); archUp.add(pivot);
  });

  // 5. Panoramic Sliding Glass Doors
  SLIDES.forEach(({rect:[x0, y0, x1, y1], v}) => {
    const L = M(v ? y1-y0 : x1-x0), ph = Math.min(v ? 2.4 : 2.1, top), pl = L*.55;
    [[-1, -.02], [1, .02]].forEach(([s, off]) => {
      const c = s < 0 ? -L/2 + pl/2 : L/2 - pl/2, x = v ? wx((x0+x1)/2) + off : wx(x0) + L/2 + c, z = v ? wz(y0) + L/2 + c : wz((y0+y1)/2) + off;
      const p = new THREE.Mesh(new THREE.BoxGeometry(v ? .02 : pl, ph, v ? pl : .02), glassMat); p.position.set(x, ph/2, z); archUp.add(p);
      [ph - .03, .03].forEach(y => { const fr = new THREE.Mesh(new THREE.BoxGeometry(v ? .04 : pl, .05, v ? pl : .04), frameMat); fr.position.set(x, y, z); archUp.add(fr); });
      [-1, 1].forEach(e => { const fr = new THREE.Mesh(new THREE.BoxGeometry(.04, ph, .04), frameMat); fr.position.set(v ? x : x + e*pl/2, ph/2, v ? z + e*pl/2 : z); archUp.add(fr); });
    });
  });

  // 6. U-Shaped Staircase & Panoramic Glass Elevator
  if (true) {
    const marbleTread = mat('#f7f4ed', {roughness: 0.2});
    const marbleRiser = mat('#d9d2c5', {roughness: 0.35});
    const brassNosing = mat('#d4af37', {metalness: 0.85, roughness: 0.25});
    const steelPost   = mat('#2b2d30', {metalness: 0.8, roughness: 0.3});
    const woodRail    = mat('#5c3a21', {roughness: 0.4});

    const flightW = 1.10;
    const treadD  = 0.30;
    const riserH  = 0.175;
    const N_STEPS = 8;
    const midLandY = N_STEPS * riserH;

    const xLeftTreadCenter  = wx(6040 + 550);
    const xRightTreadCenter = wx(9760 - 550);
    const zFlightStart = wz(14650 - 400);

    for (let i = 0; i < N_STEPS; i++) {
      const yStep = i * riserH;
      if (yStep + riserH > top) break;
      const zStep = zFlightStart - i * treadD;
      const tr = box(flightW, 0.045, treadD, marbleTread, xLeftTreadCenter, yStep + riserH - 0.045, zStep);
      const nose = box(flightW, 0.012, 0.02, brassNosing, xLeftTreadCenter, yStep + riserH - 0.012, zStep + treadD/2);
      const rs = box(flightW, riserH - 0.045, 0.03, marbleRiser, xLeftTreadCenter, yStep, zStep + treadD/2 - 0.015);
      archUp.add(tr, nose, rs);
    }

    if (midLandY <= top) {
      const midLandZ = zFlightStart - N_STEPS * treadD - 0.60;
      const midLand = box(flightW * 2 + 1.52, 0.12, 1.25, marbleTread, wx(7900), midLandY - 0.12, midLandZ);
      archUp.add(midLand);
    }

    for (let i = 0; i < N_STEPS; i++) {
      const yStep = midLandY + i * riserH;
      if (yStep + riserH > top) break;
      const zStep = (zFlightStart - N_STEPS * treadD) + i * treadD;
      const tr = box(flightW, 0.045, treadD, marbleTread, xRightTreadCenter, yStep + riserH - 0.045, zStep);
      const nose = box(flightW, 0.012, 0.02, brassNosing, xRightTreadCenter, yStep + riserH - 0.012, zStep - treadD/2);
      const rs = box(flightW, riserH - 0.045, 0.03, marbleRiser, xRightTreadCenter, yStep, zStep - treadD/2 + 0.015);
      archUp.add(tr, nose, rs);
    }

    // Panoramic Glass Elevator
    const elevX = wx(7900);
    const elevZ = wz(12650);
    const elevW = 1.52;
    const elevD = 1.50;
    const elevH = Math.min(2.80, top);

    const shaftFrameMat = mat('#1a1c1e', {metalness: 0.9, roughness: 0.2});
    const ssDoorsMat    = mat('#e2e8f0', {metalness: 0.92, roughness: 0.15});

    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => {
      const post = box(0.06, elevH, 0.06, shaftFrameMat, elevX + sx * (elevW/2 - 0.03), 0, elevZ + sz * (elevD/2 - 0.03));
      archUp.add(post);
    });

    const glassL = box(0.02, elevH, elevD - 0.08, glassMat, elevX - elevW/2 + 0.02, 0, elevZ);
    const glassR = box(0.02, elevH, elevD - 0.08, glassMat, elevX + elevW/2 - 0.02, 0, elevZ);
    const glassB = box(elevW - 0.08, elevH, 0.02, glassMat, elevX, 0, elevZ - elevD/2 + 0.02);
    archUp.add(glassL, glassR, glassB);

    const doorW = 0.42;
    const doorH = Math.min(2.15, elevH);
    const leftElevDoor  = box(doorW, doorH, 0.025, ssDoorsMat, elevX - doorW/2, 0, elevZ + elevD/2 - 0.015);
    const rightElevDoor = box(doorW, doorH, 0.025, ssDoorsMat, elevX + doorW/2, 0, elevZ + elevD/2 - 0.015);
    const callButtonBox = box(0.08, 0.18, 0.03, shaftFrameMat, elevX + elevW/2 + 0.07, 1.05, elevZ + elevD/2);
    const callLight     = box(0.025, 0.025, 0.005, mat('#38bdf8', {emissive:'#0284c7', emissiveIntensity:1.5}), elevX + elevW/2 + 0.07, 1.10, elevZ + elevD/2 + 0.016);
    archUp.add(leftElevDoor, rightElevDoor, callButtonBox, callLight);

    if (top >= 2.2) {
      const headerBox = box(0.40, 0.16, 0.04, shaftFrameMat, elevX, 2.25, elevZ + elevD/2);
      const floorInd  = box(0.24, 0.07, 0.005, mat('#0f172a', {emissive:'#38bdf8', emissiveIntensity:2.0}), elevX, 2.25, elevZ + elevD/2 + 0.022);
      archUp.add(headerBox, floorInd);
    }

    const cabinFloor = box(elevW - 0.14, 0.05, elevD - 0.14, marbleTread, elevX, 0.05, elevZ);
    const cabinCeil  = box(elevW - 0.14, 0.05, elevD - 0.14, shaftFrameMat, elevX, Math.min(2.20, elevH) - 0.05, elevZ);
    const cabinLight = new THREE.PointLight(0xf8fafc, 1.2, 3.5);
    cabinLight.position.set(elevX, Math.min(2.15, elevH) - 0.10, elevZ);
    archUp.add(cabinFloor, cabinCeil, cabinLight);
  }

  applyLight(); applyGrow();
}
"""
    content = content[:pos_build_arch_start] + new_build_arch + content[pos_build_furn_start:]

    # 13. Camera Orbit Views
    old_iso = r'const isoWhole = \(\) => \(\{x:5\.\d+, y:0, z:5\.\d+, dist:18, theta:Math\.PI\*[\d\.]+, phi:Math\.PI\*[\d\.]+\}\);'
    new_iso = 'const isoWhole = () => ({x:7.9, y:0, z:12.8, dist:32, theta:Math.PI*0.18, phi:Math.PI*0.32});'
    content = re.sub(old_iso, new_iso, content)

    old_iso_top = r'const isoTop = \(\) => \(\{x:5\.\d+, y:0, z:5\.\d+, dist:18, theta:0, phi:0\.001\}\);'
    new_iso_top = 'const isoTop = () => ({x:7.9, y:0, z:12.8, dist:32, theta:0, phi:0.001});'
    content = re.sub(old_iso_top, new_iso_top, content)

    # 14. Save Files
    with open(house_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("MASTER BUILD COMPLETE!")
    print(f"Generated {len(walls)} walls, {len(wins)} windows, {len(doors)} doors, {len(slides)} sliding doors.")
    print(f"Generated {len(rooms)} rooms, {len(furniture)} furniture items.")

if __name__ == '__main__':
    generate_master_apartment()
