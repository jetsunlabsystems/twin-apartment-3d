# -*- coding: utf-8 -*-
import json
import re
import os

from generate_luxury_twin_arabic import build_refined_house

def build_everything():
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
    
    old_css_font = 'font:13px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif'
    new_css_font = "font:14px/1.6 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    content = content.replace(old_css_font, new_css_font)
    
    old_btn_font = 'button,input,select{font:inherit;color:inherit}'
    new_btn_font = "button,input,select{font-family:'Tajawal',inherit;font-size:inherit;color:inherit}"
    content = content.replace(old_btn_font, new_btn_font)
    
    old_svg_font = 'font-family="-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif"'
    new_svg_font = 'font-family="\'Tajawal\', -apple-system, sans-serif"'
    content = content.replace(old_svg_font, new_svg_font)

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
    ]

    for zh, ar in html_replacements:
        content = content.replace(zh, ar)

    # 3. Clean CSS for `.rlabel` (Readable, non-clutter badges)
    old_rlabel_css = """.rlabel{font-size:12px;font-weight:600;color:#2b2824;background:rgba(255,253,249,.9);border:1px solid var(--line);
  border-radius:12px;padding:2px 9px;white-space:nowrap;pointer-events:none}
.rlabel small{font-weight:400;color:var(--muted);margin-left:4px}"""

    new_rlabel_css = """.rlabel{font-family:'Tajawal',sans-serif;font-size:12px;font-weight:700;color:#1e293b;background:rgba(255,255,255,0.92);
  border:1px solid rgba(0,0,0,0.12);border-radius:20px;padding:3px 10px;white-space:nowrap;pointer-events:none;
  box-shadow:0 3px 10px rgba(0,0,0,0.08);backdrop-filter:blur(4px);display:flex;align-items:center;gap:6px}
.rlabel small{font-weight:500;color:#b5653a;background:rgba(181,101,58,0.1);padding:1px 6px;border-radius:10px;font-size:11px}"""
    content = content.replace(old_rlabel_css, new_rlabel_css)

    # 4. Replace Language Engine block strictly (from /* ======================= 多语言 down to applyStaticLang() end)
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
  curLang = l;
  localStorage.setItem('app_lang', l);
  document.documentElement.lang = l === 'zh' ? 'ar' : 'en';
  document.documentElement.dir = l === 'zh' ? 'rtl' : 'ltr';
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
    const on = (b.dataset.lang === curLang) || (b.dataset.lang === 'zh' && curLang === 'zh');
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
}"""

    content = content[:idx_lang_start] + clean_lang_engine + content[idx_lang_end:]

    # 5. Materials (MATS)
    old_mats = """const MATS = {
  wood:    {name:'橡木地板', price:320, sw:'#d8b88a'},
  walnut:  {name:'胡桃木地板', price:380, sw:'#9b7250'},
  tile800: {name:'800 地砖', price:220, sw:'#ebe6dc'},
  tile600: {name:'600 地砖', price:160, sw:'#dfe3e1'},
  marble:  {name:'大理石', price:650, sw:'#f1eee8'},
  antislip:{name:'300 防滑砖', price:140, sw:'#d3d8d4'},
  terrazzo:{name:'水磨石', price:280, sw:'#e6dfd3'},
  carpet:  {name:'满铺地毯', price:200, sw:'#c9c3d3'},
};"""

    new_mats = """const MATS = {
  marble:  {name:{zh:'رخام إيطالي كالاتا مصقول', en:'Polished Italian Calacatta Marble'}, price:680, sw:'#f6f3ee'},
  wood:    {name:{zh:'باركيه خشب بلوط فرنسي فاخر', en:'French Oak Natural Parquet'}, price:380, sw:'#c9985d'},
  walnut:  {name:{zh:'باركيه خشب جوز ملكي داكن', en:'Dark American Walnut Flooring'}, price:420, sw:'#724c30'},
  tile800: {name:{zh:'بورسلان بيج دافئ كبير 800×800', en:'Warm Ivory Porcelain Tiles 800x800'}, price:240, sw:'#ebe5d9'},
  tile600: {name:{zh:'بورسلان رمادي حجري للمطبخ 600×600', en:'Modern Slate Kitchen Tiles 600x600'}, price:190, sw:'#596168'},
  antislip:{name:{zh:'حجر مانع للانزلاق للحمامات', en:'Textured Non-Slip Bathroom Stone'}, price:170, sw:'#3d444b'},
  terrazzo:{name:{zh:'تيرازو فينيسي مودرن للتراس', en:'Venetian Terrazzo Balcony Tiles'}, price:290, sw:'#e4ddcf'},
  carpet:  {name:{zh:'سجاد صوف فاخر', en:'Plush Wool Carpet'}, price:220, sw:'#b8b0c4'},
};"""
    content = content.replace(old_mats, new_mats)

    # 6. Replace WALLS, BOUNDS, WINS, DOORS, SLIDES, ROOMS
    bounds_json = json.dumps({
        "x": -1000,
        "y": -1000,
        "w": 17800,
        "h": 27700
    })

    model_data_block = f"""const BOUNDS = {bounds_json};
const WALLS = {json.dumps(walls, indent=2, ensure_ascii=False)};
const WINS = {json.dumps(wins, indent=2, ensure_ascii=False)};
const DOORS = {json.dumps(doors, indent=2, ensure_ascii=False)};
const SLIDES = {json.dumps(slides, indent=2, ensure_ascii=False)};
const ROOMS = {json.dumps(rooms, indent=2, ensure_ascii=False)};"""

    pattern_model_data = r'const BOUNDS\s*=\s*\{[^}]+\};\s*const WALLS\s*=\s*\[[\s\S]*?const ROOMS\s*=\s*\[[\s\S]*?\];'
    # Use lambda to prevent re.sub from interpreting backslashes
    content = re.sub(pattern_model_data, lambda m: model_data_block, content, count=1)

    # 7. Default Furniture
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
}}"""
    pattern_default_furn = r'function defaultFurniture\(\)\{[\s\S]*?return\s*\[[\s\S]*?\];\s*\}'
    content = re.sub(pattern_default_furn, lambda m: new_default_furniture, content, count=1)

    # 8. Update storage key to ensure users get the new luxury setup immediately
    content = content.replace("const STORE = 'floorplan-3d-v4';", "const STORE = 'twin-apartment-luxury-v2';")
    content = content.replace("const STORE = 'twin-apartment-house-3d-v5';", "const STORE = 'twin-apartment-luxury-v2';")

    # 9. Camera setup for grand apartment view
    old_iso = r'const isoWhole = \(\) => \(\{x:5\.\d+, y:0, z:5\.\d+, dist:18, theta:Math\.PI\*[\d\.]+, phi:Math\.PI\*[\d\.]+\}\);'
    new_iso = 'const isoWhole = () => ({x:7.9, y:0, z:12.8, dist:32, theta:Math.PI*0.18, phi:Math.PI*0.32});'
    content = re.sub(old_iso, new_iso, content)

    old_iso_top = r'const isoTop = \(\) => \(\{x:5\.\d+, y:0, z:5\.\d+, dist:18, theta:0, phi:0\.001\}\);'
    new_iso_top = 'const isoTop = () => ({x:7.9, y:0, z:12.8, dist:32, theta:0, phi:0.001});'
    content = re.sub(old_iso_top, new_iso_top, content)

    # 10. Floor Materials Procedural Textures (TEX)
    old_tex_block = content[content.find("const TEX = {"):content.find("/* ======================= 几何小工具")]
    
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
        // Dark plank bevel joint
        g.fillStyle = rgbK(s.base, .55); g.fillRect(x1-2, r*rowH, 4, rowH); x0 = x1;
      });
      g.fillStyle = rgbK(s.base, .55); g.fillRect(0, r*rowH, W, 3.5);
    }
  } else if (kind === 'marble'){
    // High-end Calacatta marble with delicate branching veins and subtle clouding
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
    // Subtle tile grout bevel lines
    g.fillStyle = s.grout; g.fillRect(0, 0, W, 4); g.fillRect(0, 0, 4, Hh);
    g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillRect(4, 4, W-4, 2); g.fillRect(4, 4, 2, Hh-4);
  } else if (kind === 'terrazzo'){
    const cs = ['#b9a58c','#8fa3a0','#c9b7a2','#a88f76','#7e8a86','#ffffff'];
    for (let k = 0; k < 280; k++){
      g.fillStyle = cs[k%cs.length]; g.beginPath(); g.arc(R()*W, R()*Hh, 2 + R()*8, 0, 7); g.fill();
    }
    if (s.grout){ g.fillStyle = s.grout; g.fillRect(0, 0, W, 4); g.fillRect(0, 0, 4, Hh); }
  } else {
    // Ceramic and porcelain tiles with contrasting crisp grout
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
    content = content.replace(old_tex_block, new_tex_block)

    # 11. Architectural Windows, Millwork Doors, Balustrades & Stairs/Elevator in `buildArch`
    old_build_arch = content[content.find("function buildArch(){"):content.find("function buildFurn(){")]

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
    // Ceiling: visible looking up in walk mode
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
      // Luxury entrance security door with dark bronze horizontal insets & tall vertical pull handle
      for (let k = 0; k < 4; k++){
        leaf.add(box(L * 0.72, 0.012, 0.048, mat('#151210', {roughness:.2, metalness:.8}), L/2, 0.4 + k * 0.42, 0));
      }
      const handleBar = cyl(0.014, 0.014, 0.65, metal('#e2e8f0'), L - 0.12, 0.7, 0.045);
      const post1 = box(0.02, 0.02, 0.04, metal(), L - 0.12, 0.75, 0.025);
      const post2 = box(0.02, 0.02, 0.04, metal(), L - 0.12, 1.25, 0.025);
      leaf.add(handleBar, post1, post2);
    } else {
      // Modern interior room door with horizontal routing & chrome lever handle
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

    // Left Flight (Climbing to mid-landing)
    for (let i = 0; i < N_STEPS; i++) {
      const yStep = i * riserH;
      if (yStep + riserH > top) break;
      const zStep = zFlightStart - i * treadD;
      const tr = box(flightW, 0.045, treadD, marbleTread, xLeftTreadCenter, yStep + riserH - 0.045, zStep);
      const nose = box(flightW, 0.012, 0.02, brassNosing, xLeftTreadCenter, yStep + riserH - 0.012, zStep + treadD/2);
      const rs = box(flightW, riserH - 0.045, 0.03, marbleRiser, xLeftTreadCenter, yStep, zStep + treadD/2 - 0.015);
      archUp.add(tr, nose, rs);
    }

    // Mid Landing
    if (midLandY <= top) {
      const midLandZ = zFlightStart - N_STEPS * treadD - 0.60;
      const midLand = box(flightW * 2 + 1.52, 0.12, 1.25, marbleTread, wx(7900), midLandY - 0.12, midLandZ);
      archUp.add(midLand);
    }

    // Right Flight (Climbing to upper floor)
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

    // 4 Corner Steel Posts
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => {
      const post = box(0.06, elevH, 0.06, shaftFrameMat, elevX + sx * (elevW/2 - 0.03), 0, elevZ + sz * (elevD/2 - 0.03));
      archUp.add(post);
    });

    // Glass Enclosures
    const glassL = box(0.02, elevH, elevD - 0.08, glassMat, elevX - elevW/2 + 0.02, 0, elevZ);
    const glassR = box(0.02, elevH, elevD - 0.08, glassMat, elevX + elevW/2 - 0.02, 0, elevZ);
    const glassB = box(elevW - 0.08, elevH, 0.02, glassMat, elevX, 0, elevZ - elevD/2 + 0.02);
    archUp.add(glassL, glassR, glassB);

    // Front Sliding Doors & Call Indicator
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

    // Elevator Cabin
    const cabinFloor = box(elevW - 0.14, 0.05, elevD - 0.14, marbleTread, elevX, 0.05, elevZ);
    const cabinCeil  = box(elevW - 0.14, 0.05, elevD - 0.14, shaftFrameMat, elevX, Math.min(2.20, elevH) - 0.05, elevZ);
    const cabinLight = new THREE.PointLight(0xf8fafc, 1.2, 3.5);
    cabinLight.position.set(elevX, Math.min(2.15, elevH) - 0.10, elevZ);
    archUp.add(cabinFloor, cabinCeil, cabinLight);
  }

  applyLight(); applyGrow();
}
"""
    content = content.replace(old_build_arch, new_build_arch)

    # 12. Save house-3d.html and index.html
    with open(house_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("SUCCESS: Generated luxury twin-apartment with high-end floors, windows, doors, and full furniture!")
    print(f"- Walls: {len(walls)}")
    print(f"- Windows: {len(wins)}")
    print(f"- Doors: {len(doors)}")
    print(f"- Sliding Glass Doors: {len(slides)}")
    print(f"- Rooms: {len(rooms)}")
    print(f"- Furniture items: {len(furniture)}")

if __name__ == '__main__':
    build_everything()
