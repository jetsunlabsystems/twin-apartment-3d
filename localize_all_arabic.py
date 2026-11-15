import re
import os

def run():
    base_dir = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d"
    house_path = os.path.join(base_dir, "house-3d.html")
    index_path = os.path.join(base_dir, "index.html")

    with open(house_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace translation engine (lines 348 to 386)
    pattern_engine = r"/\* =+ 多语言[\s\S]*?function applyStaticLang\(\)\{[\s\S]*?\}\n\}"
    new_engine = """/* ======================= اللغة (العربية / English - الافتراضي: العربية) ======================= */
const LANG_KEY = 'twin-apartment-lang-ar-v2';
const LANGS = ['ar', 'en'];
let LANG = (() => { try { const l = localStorage.getItem(LANG_KEY); return LANGS.includes(l) ? l : 'ar'; } catch(e) { return 'ar'; } })();

const tr = (ar, en) => LANG === 'en' ? en : ar;

const NAMES_EN = {
  'غرف النوم':'Bedrooms', 'الصالون والمعيشة':'Living Room', 'المطبخ وتناول الطعام':'Dining & Kitchen',
  'الحمامات':'Bathrooms', 'الأجهزة المنزلية':'Appliances', 'المكتب والترفيه':'Study & Leisure',
  'خشب باركيه بلوط':'Oak Flooring', 'خشب باركيه جوز فاخر':'Walnut Flooring', 'بورسلين 80×80':'800 Porcelain Tile',
  'سيراميك 60×60':'600 Ceramic Tile', 'رخام كلكتا إيطالي فاخر':'Calacatta Italian Marble', 'بلاط حجري مانع للانزلاق':'Anti-slip Stone Tile',
  'تيرازو مصقول':'Polished Terrazzo', 'موكيت سجاد فاخر':'Luxury Carpet',
  'نوم رئيسية (Master L)':'Master Bedroom (L)', 'حمام ماستر (Bath L)':'Master Bath (L)', 'ملابس (Closet L)':'Walk-in Closet (L)',
  'نوم 2 (Bed 2 L)':'Bedroom 2 (L)', 'غسيل (Laundry L)':'Laundry Room (L)', 'حمام عائلي (Bath L)':'Family Bath (L)',
  'نوم 1 (Bed 1 L)':'Bedroom 1 (L)', 'معيشة (Living L)':'Living Room (L)', 'مطبخ (Kitchen L)':'Kitchen (L)',
  'حمام ضيوف (Guest Bath L)':'Guest Bath (L)', 'استقبال (Reception L)':'Reception Salon (L)', 'تراس (Terrace L)':'Terrace (L)',
  'نوم رئيسية (Master R)':'Master Bedroom (R)', 'حمام ماستر (Bath R)':'Master Bath (R)', 'ملابس (Closet R)':'Walk-in Closet (R)',
  'نوم 2 (Bed 2 R)':'Bedroom 2 (R)', 'غسيل (Laundry R)':'Laundry Room (R)', 'حمام عائلي (Bath R)':'Family Bath (R)',
  'نوم 1 (Bed 1 R)':'Bedroom 1 (R)', 'معيشة (Living R)':'Living Room (R)', 'مطبخ (Kitchen R)':'Kitchen (R)',
  'حمام ضيوف (Guest Bath R)':'Guest Bath (R)', 'استقبال (Reception R)':'Reception Salon (R)', 'تراس (Terrace R)':'Terrace (R)',
  'منور (Lightwell)':'Lightwell', 'درج ومصعد (Stairs & Elevator)':'Stairs & Elevator Core',
  'سرير ماستر 1.8m':'Master Bed 1.8m', 'سرير 1.5m':'Bed 1.5m', 'سرير مفرد':'Single Bed',
  'كومودينو':'Nightstand', 'دولاب ملابس':'Wardrobe', 'مكتب دراسة':'Study Desk', 'كرسي':'Chair',
  'كنبة 3 مقاعد':'3-Seat Sofa', 'طاولة رخام':'Marble Coffee Table', 'سجادة صالون فاخرة':'Luxury Rug',
  'كنبة زاوية عائلية':'Family Corner Sofa', 'طقم استقبال 3 مقاعد':'Reception Sofa 3-Seat',
  'رخام مطبخ كاونتر':'Kitchen Countertop', 'بوتاجاز غاز':'Gas Stove', 'حوض غسيل':'Kitchen Sink', 'ثلاجة عائلية':'Family Refrigerator',
  'طاولة طعام 4 كراسي':'Dining Table 4-Seat', 'طاولة طعام 6 مقاعد':'Dining Table 6-Seat', 'طاولة طعام دائرية':'Round Dining Table',
  'كرسي طعام':'Dining Chair', 'جزيرة مطبخ رخامية':'Kitchen Island', 'كرسي بار مرتفع':'Bar Stool',
  'مرحاض معلق':'Wall-hung Toilet', 'وحدة حوض حمام':'Bathroom Vanity', 'وحدة حوض مزدوجة':'Double Vanity',
  'كابينة شاور':'Glass Shower', 'حوض استحمام بانيو':'Bathtub', 'غسالة ملابس':'Washing Machine', 'سخان مياه':'Water Heater',
  'شاشة تلفزيون 65 بوصة':'65" 4K TV', 'شاشة تلفزيون 55 بوصة':'55" 4K TV', 'مكيف سبليت':'Split AC', 'مكيف دولابي عمودي':'Tower AC',
  'غسالة أطباق':'Dishwasher', 'دولاب أفران مدمجة':'Built-in Oven Tower', 'مجفف ملابس':'Dryer', 'منقي هواء':'Air Purifier',
  'طاولة مكتب عمل':'Office Desk', 'كرسي مكتب تنفيذي':'Executive Chair', 'خزانة كتب جدارية':'Wall Bookshelf',
  'بيانو كلاسيكي':'Upright Piano', 'جهاز سير رياضي':'Treadmill', 'كرسي قراءة واسترخاء':'Reading Chair',
  'طاولة شاي وجلسة':'Tea Table', 'كرسي استرخاء شيزلونج':'Lounge Chair',
  'كامل المبنى':'Whole Building'
};

const nm = s => LANG === 'en' ? (NAMES_EN[s] ?? s) : s;

function applyStaticLang(){
  document.documentElement.lang = LANG;
  document.documentElement.dir = LANG === 'ar' ? 'rtl' : 'ltr';
  document.title = tr('عمارة سكنية فاخرة · شقتين متطابقتين (3D)', 'Twin Luxury Apartments 3D Floor Plan');
  document.querySelectorAll('[data-en]').forEach(el => {
    el.dataset.ar ??= el.textContent;
    el.textContent = tr(el.dataset.ar, el.dataset.en);
  });
  document.querySelectorAll('[data-en-title]').forEach(el => {
    el.dataset.arTitle ??= el.title;
    el.title = tr(el.dataset.arTitle, el.dataset.enTitle);
  });
  document.querySelectorAll('#langSel [data-lang]').forEach(b => {
    const on = b.dataset.lang === LANG;
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
}"""
    content = re.sub(pattern_engine, new_engine, content)

    # 2. defaultFurniture
    content = content.replace("F('tv','65 寸电视',4000,12700,1450,80,180),", "F('tv','شاشة تلفزيون 65 بوصة',4000,12700,1450,80,180),")

    # 3. Subtitle
    old_sub = "  $('#subtitle').textContent = tr(`套内使用面积约 ${fmt(tot)} m² · 尺寸单位 mm · 原图比例 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`);"
    new_sub = "  $('#subtitle').textContent = tr(`إجمالي المساحة الصافية حوالي ${fmt(tot)} م² · الأبعاد بالمليمتر · مقياس 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`);"
    content = content.replace(old_sub, new_sub)

    # 4. Touch Help Table
    pattern_touch = r"\$\{COARSE \? tr\(`<section><h3>触屏操作</h3>[\s\S]*?`\) : ''\}"
    new_touch = """${COARSE ? tr(`<section><h3>إيماءات اللمس</h3><div class="kbd">
    <kbd>سحب بإصبع</kbd><span>تحريك المخطط في المساحات الفارغة</span><kbd>إصبعان</kbd><span>تكبير وتصغير وتحريك المخطط</span>
    <kbd>مكتبة الأثاث</kbd><span>اضغط للإضافة في المركز، أو اسحب لموضع معين</span>
    <kbd>تحديد الأثاث</kbd><span>اسحب للتحريك؛ اسحب النقطة للتدوير، والزاوية للحجم</span>
    <kbd>شريط الأدوات</kbd><span>خيارات التدوير / التكرار / الحذف بالأسفل</span>
    <kbd>القياس</kbd><span>اسحب لرسم خط القياس، أو انقر نقطتين</span>
    <kbd>جولة 3D</kbd><span>عصا التحكم باليسار للحركة، اسحب للنظر، انقر الأبواب للفتح</span>
  </div></section>`, `<section><h3>Touch Controls</h3><div class="kbd">
    <kbd>1-finger drag</kbd><span>Pan the canvas</span><kbd>2-finger</kbd><span>Pinch to zoom / pan</span>
    <kbd>Library</kbd><span>Tap to place in center, or drag to target</span>
    <kbd>Tap item</kbd><span>Drag to move; drag top dot to rotate, corner to resize</span>
    <kbd>Toolbar</kbd><span>Rotate / duplicate / delete at bottom</span>
    <kbd>Measure</kbd><span>Drag a line or tap two points</span>
    <kbd>3D walk</kbd><span>Joystick moves, drag screen looks, tap doors</span>
  </div></section>`) : ''}"""
    content = re.sub(pattern_touch, new_touch, content)

    # 5. Keyboard shortcuts table
    pattern_kbd = r"\$\{tr\(`<section><h3>键盘快捷键</h3>[\s\S]*?`\)\}"
    new_kbd = """${tr(`<section><h3>اختصارات لوحة المفاتيح</h3><div class="kbd">
    <kbd>سحب الأثاث</kbd><span>اسحب من المكتبة إلى المخطط</span><kbd>V</kbd><span>تحديد / تحريك</span><kbd>M</kbd><span>قياس الأبعاد (Shift للأفقي/العمودي)</span>
    <kbd>X</kbd><span>تعديل الجدران (الأسود جدار حامل)</span><kbd>R</kbd><span>تدوير 90° (Shift للعكس)</span><kbd>الأسهم</kbd><span>تحريك دقيق 10mm (مع Shift 100mm)</span>
    <kbd>Ctrl+D</kbd><span>تكرار العنصر</span><kbd>Delete</kbd><span>حذف</span><kbd>Ctrl+Z</kbd><span>تراجع</span><kbd>T</kbd><span>تبديل 2D / 3D</span><kbd>F</kbd><span>ملاءمة الشاشة</span><kbd>Esc</kbd><span>إلغاء التحديد</span>
  </div></section>`, `<section><h3>Keyboard Shortcuts</h3><div class="kbd">
    <kbd>Drag</kbd><span>Drag furniture onto the plan</span><kbd>V</kbd><span>Select / move</span><kbd>M</kbd><span>Measure (Shift: horizontal/vertical)</span>
    <kbd>X</kbd><span>Demolish non-bearing walls</span><kbd>R</kbd><span>Rotate 90° (Shift: reverse)</span><kbd>Arrow keys</kbd><span>Nudge 10mm (Shift: 100mm)</span>
    <kbd>Ctrl+D</kbd><span>Duplicate</span><kbd>Delete</kbd><span>Delete</span><kbd>Ctrl+Z</kbd><span>Undo</span><kbd>T</kbd><span>Toggle 2D / 3D</span><kbd>F</kbd><span>Fit to window</span><kbd>Esc</kbd><span>Deselect</span>
  </div></section>`)}"""
    content = re.sub(pattern_kbd, new_kbd, content)

    # 6. Confirm dialog
    old_confirm = "if (!confirm(tr(`确定清空全部 ${n} 件家具 / 家电吗？\\n墙体、地面材料和测量线会保留，可点「撤销」恢复。`, `Remove all ${n} furniture / appliance items?\\nWalls, flooring and measurements are kept. You can Undo this.`))) return;"
    new_confirm = "if (!confirm(tr(`هل أنت متأكد من تفريغ كافة قطع الأثاث (${n} قطعة)؟\\nالجدران، خامات الأرضيات، وخطوط القياس ستبقى، ويمكن التراجع.`, `Remove all ${n} furniture / appliance items?\\nWalls, flooring and measurements are kept. You can Undo this.`))) return;"
    content = content.replace(old_confirm, new_confirm)

    # 7. Wall Area
    old_wall = "<div class=\"muted\">${tr(`墙面面积（层高 2.8m，未扣门窗）约 ${fmt(perim(r.poly)*2.8,1)} m²`, `Wall area (2.8m ceiling, openings not deducted) ≈ ${fmt(perim(r.poly)*2.8,1)} m²`)}</div></section>"
    new_wall = "<div class=\"muted\">${tr(`مساحة الجدران (ارتفاع 2.8m، دون خصم الفتحات) حوالي ${fmt(perim(r.poly)*2.8,1)} م²`, `Wall area (2.8m ceiling, openings not deducted) ≈ ${fmt(perim(r.poly)*2.8,1)} m²`)}</div></section>"
    content = content.replace(old_wall, new_wall)

    # 8. Furniture properties labels
    content = content.replace("<label>${tr('颜色','Color')}<input", "<label>${tr('اللون','Color')}<input")
    content = content.replace("<div class=\"muted\" style=\"margin-top:8px\">${tr('占地面积','Footprint')}", "<div class=\"muted\" style=\"margin-top:8px\">${tr('المساحة المشغولة','Footprint')}")
    
    old_snap_tip = '<section class="muted" style="font-size:12px">${tr(\'拖动家具移动；拖动上方圆点旋转；拖动右下角方块调整尺寸。开启「贴墙吸附」后靠近墙面会自动贴齐。\', \'Drag to move; drag the top dot to rotate; drag the bottom-right square to resize. With "Wall snap" on, items snap flush to nearby walls.\')}</section>'
    new_snap_tip = '<section class="muted" style="font-size:12px">${tr(\'اسحب القطعة للتحريك، اسحب النقطة العلوية للتدوير، واسحب الزاوية لتعديل المقاس. تفعيل «محاذاة للجدار» يجعل الأثاث يلتصق بالجدار تلقائياً.\', \'Drag to move; drag the top dot to rotate; drag the bottom-right square to resize. With "Wall snap" on, items snap flush to nearby walls.\')}</section>'
    content = content.replace(old_snap_tip, new_snap_tip)

    # 9. Demolish wall toast
    old_dem_toast = 'toast(on ? tr(\'تمت استعادة الجدار\', \'Wall restored\') : tr(`已标记拆除 ${Math.max(w[2]-w[0], w[3]-w[1])} mm 墙体`, `Marked ${Math.max(w[2]-w[0], w[3]-w[1])} mm of wall for removal`));'
    new_dem_toast = 'toast(on ? tr(\'تمت استعادة الجدار\', \'Wall restored\') : tr(`تم تحديد إزالة ${Math.max(w[2]-w[0], w[3]-w[1])} mm من الجدار`, `Marked ${Math.max(w[2]-w[0], w[3]-w[1])} mm of wall for removal`));'
    content = content.replace(old_dem_toast, new_dem_toast)

    # 10. Measure and Demolish hints
    old_md_hints = """    measure:COARSE ? tr('按住拖出测量线，或依次点两点 · 靠近墙面自动吸附 · 点「选择」退出', 'Hold and drag a line, or tap two points · snaps to walls · tap "Select" to exit')
      : tr('点击两点（或按住拖动）测量距离 · 靠近墙面自动吸附 · Shift 锁定水平/垂直 · Esc 取消', 'Click two points (or drag) to measure · snaps to walls · Shift locks horizontal/vertical · Esc cancels'),
    demolish:tr('点击灰色非承重墙标记拆除，再次点击恢复 · 黑色承重墙不可拆', 'Click a grey non-bearing wall to remove it, click again to restore · black bearing walls cannot be removed')};"""

    new_md_hints = """    measure:COARSE ? tr('اسحب لرسم خط القياس، أو انقر نقطتين · محاذاة تلقائية للجدران · اضغط «تحديد» للخروج', 'Hold and drag a line, or tap two points · snaps to walls · tap "Select" to exit')
      : tr('انقر نقطتين (أو اسحب) لقياس المسافة · محاذاة تلقائية للجدران · Shift لقفل الاتجاه أفقي/عمودي · Esc للإلغاء', 'Click two points (or drag) to measure · snaps to walls · Shift locks horizontal/vertical · Esc cancels'),
    demolish:tr('انقر على الجدار غير الحامل لتحديده للإزالة، وانقر ثانية للاستعادة · الجدران الحاملة الإنشائية لا يمكن إزالتها', 'Click a grey non-bearing wall to remove it, click again to restore · black bearing walls cannot be removed')};"""
    content = content.replace(old_md_hints, new_md_hints)

    # 11. Library item title & description
    old_lib_item = 'return `<div class="item" data-key="${ci}:${ii}" title="${tr(\'点击添加，或拖到平面图中的指定位置\', \'Click to add, or drag onto the plan\')}">'
    new_lib_item = 'return `<div class="item" data-key="${ci}:${ii}" title="${tr(\'اضغط للإضافة، أو اسحب للموضع المطلوب في المخطط\', \'Click to add, or drag onto the plan\')}">'
    content = content.replace(old_lib_item, new_lib_item)

    old_lib_desc = "`家具按真实尺寸（mm）绘制。${COARSE ? '点一下放到画面中央，或按住向右拖到平面图 / 3D 地面上的指定位置（上下滑动为滚动列表）。' : '点击添加到画面中央，或直接拖到平面图 / 3D 地面上。'}添加后可在右侧修改宽深与颜色。`"
    new_lib_desc = "`الأثاث مرسوم بمقاساته الحقيقية (mm). ${COARSE ? 'اضغط للإضافة في المركز، أو اسحب للموضع المطلوب داخل المخطط.' : 'اضغط للإضافة في المركز، أو اسحب مباشرة إلى المخطط أو المشهد ثلاثي الأبعاد.'} يمكنك تعديل المقاسات والألوان من لوحة الخصائص.`"
    content = content.replace(old_lib_desc, new_lib_desc)

    # 12. Fullscreen toast
    old_fs = 'if (!req) return toast(tr(\'当前浏览器不支持网页全屏，可在 Safari 中「添加到主屏幕」后以全屏方式打开\', \'Fullscreen is not supported here — in Safari, use "Add to Home Screen" to open it fullscreen\'));'
    new_fs = 'if (!req) return toast(tr(\'المتصفح الحالي لا يدعم وضع ملء الشاشة، يمكن إضافته للشاشة الرئيسية للاستمتاع بملء الشاشة\', \'Fullscreen is not supported here — in Safari, use "Add to Home Screen" to open it fullscreen\'));'
    content = content.replace(old_fs, new_fs)

    # 13. CSS Comment
    content = content.replace('/* 收起动画中内容不被挤压变形 */', '/* Prevent content squeezing during collapse */')

    with open(house_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Complete Arabic Tajawal localization succeeded for both files!")

if __name__ == '__main__':
    run()
