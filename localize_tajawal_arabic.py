import re
import os

def localize_content(content):
    # 1. HTML Header and Font: Add Google Font Tajawal
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
    
    # 2. Font styling in CSS
    old_css_font = 'font:13px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif'
    new_css_font = "font:14px/1.6 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    content = content.replace(old_css_font, new_css_font)
    
    old_btn_font = 'button,input,select{font:inherit;color:inherit}'
    new_btn_font = "button,input,select{font-family:'Tajawal',inherit;font-size:inherit;color:inherit}"
    content = content.replace(old_btn_font, new_btn_font)
    
    old_svg_font = 'font-family="-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif"'
    new_svg_font = 'font-family="\'Tajawal\', -apple-system, sans-serif"'
    content = content.replace(old_svg_font, new_svg_font)
    
    # 3. Header HTML Elements (Translate Chinese to Arabic)
    html_replacements = [
        # Library / Panel buttons
        ('>◧ 家具库<', '>◧ مكتبة الأثاث<'),
        ('>属性 ◨<', '>الخصائص ◨<'),
        ('data-en="◧ Library">◧ 家具库<', 'data-en="◧ Library">◧ مكتبة الأثاث<'),
        ('data-en="Properties ◨">属性 ◨<', 'data-en="Properties ◨">الخصائص ◨<'),
        
        # Brand & Subtitle
        ('三室两厅两卫 · 装修设计', 'عمارة سكنية فاخرة · شقتين متطابقتين'),
        ('data-en="3BR 2LR 2BA · Interior Design">三室两厅两卫 · 装修设计<', 'data-en="Luxury Twin Apartments · 3D Design">عمارة سكنية فاخرة · شقتين متطابقتين<'),
        ('原始户型 1:60 · 尺寸单位 mm', 'مخطط معماري تفاعلي 1:60 · الأبعاد بالمليمتر (mm)'),
        
        # 2D / 3D Segments
        ('title="切换 2D / 3D (T)"', 'title="تبديل 2D / 3D (T)"'),
        ('>2D 平面<', '>مخطط 2D<'),
        ('>3D 场景<', '>مشهد 3D<'),
        
        # Tools
        ('title="选择 / 移动 (V)"', 'title="تحديد / تحريك (V)"'),
        ('>选择<', '>تحديد<'),
        ('title="测量 (M)"', 'title="قياس الأبعاد (M)"'),
        ('>测量<', '>قياس<'),
        ('title="拆改非承重墙 (X)"', 'title="تعديل الجدران (X)"'),
        ('>拆改墙体<', '>تعديل الجدران<'),
        
        # Zoom / Scale
        ('title="缩小"', 'title="تصغير"'),
        ('title="放大"', 'title="تكبير"'),
        ('title="适应窗口 (F)"', 'title="ملاءمة الشاشة (F)"'),
        ('>适应<', '>ملاءمة<'),
        ('title="按 1:60 显示（与原图同比例）"', 'title="عرض بمقياس 1:60 (مطابق للمخطط الأصلي)"'),
        ('title="按 1:100 显示"', 'title="عرض بمقياس 1:100"'),
        
        # 3D Modes
        ('>鸟瞰<', '>منظور علوي<'),
        ('>漫游<', '>جولة 3D<'),
        ('>斜视<', '>منظور مائل<'),
        ('>俯视<', '>مسقط رأسي<'),
        
        # Undo / Redo / Clear
        ('title="撤销 (Ctrl+Z)"', 'title="تراجع (Ctrl+Z)"'),
        ('>撤销<', '>تراجع<'),
        ('title="重做 (Ctrl+Shift+Z)"', 'title="إعادة (Ctrl+Shift+Z)"'),
        ('>重做<', '>إعادة<'),
        ('title="清空所有家具家电（可撤销）"', 'title="إفراغ جميع الأثاث (يمكن التراجع)"'),
        ('>清空布置<', '>إفراغ التأثيث<'),
        
        # 2D Layers
        ('>尺寸<', '>الأبعاد<'),
        ('>房间<', '>الغرف<'),
        ('>家具<', '>الأثاث<'),
        ('>网格<', '>الشبكة<'),
        ('>承重墙<', '>جدران حاملة<'),
        ('title="拖动家具时贴墙吸附"', 'title="محاذاة ومغناطيسية للجدران أثناء السحب"'),
        ('>贴墙吸附<', '>محاذاة للجدار<'),
        
        # 3D Cutaway
        ('>全高墙<', '>جدران كاملة<'),
        ('>剖切墙<', '>مقطع جدران<'),
        
        # 3D Toggles
        ('>房间名<', '>أسماء الغرف<'),
        ('>夜景<', '>وضع ليلي<'),
        ('>日照<', '>الشمس<'),
        
        # Language Selector
        ('<button class="btn chip" data-lang="zh" title="简体中文">简</button>\n      <button class="btn chip" data-lang="zht" title="繁體中文">繁</button>\n      <button class="btn chip" data-lang="en" title="English">EN</button>',
         '<button class="btn chip on" data-lang="ar" title="العربية">عربي</button>\n      <button class="btn chip" data-lang="en" title="English">EN</button>'),
        ('aria-label="Language / 语言"', 'aria-label="Language / اللغة"'),
        
        # Fullscreen & Menu
        ('title="全屏 (Shift+F)"', 'title="ملء الشاشة (Shift+F)"'),
        ('>⛶ 全屏<', '>⛶ ملء الشاشة<'),
        ('>文件 ▾<', '>ملف ▾<'),
        ('>导出图片<', '>تصدير صورة PNG<'),
        ('>导出方案 JSON<', '>تصدير المخطط JSON<'),
        ('>导入方案<', '>استيراد مخطط<'),
        ('>重置为默认方案<', '>استعادة المخطط الافتراضي<'),
        
        # Aside / Walkthrough overlay
        ('>房间 · 点击飞到该房间<', '>الغرف · اضغط للانتقال إليها<'),
        ('>漫游模式<', '>وضع الجولة الافتراضية<'),
        ('>退出漫游<', '>إنهاء الجولة<'),
        ('>当前比例<', '>المقياس<'),
    ]
    
    for old_s, new_s in html_replacements:
        content = content.replace(old_s, new_s)
        
    # 4. Replace translation engine (LANG, S2T, tr, applyStaticLang)
    old_lang_engine_pattern = r"/\* =+ 多语言.*?function applyStaticLang\(\)\{[\s\S]*?applyStaticLang\(\); syncFullscreen\(\);"
    
    new_lang_engine = """/* ======================= اللغة (العربية / English - الافتراضي: العربية) ======================= */
const LANG_KEY = 'twin-house-lang-v2';
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
  'طاولة طعام':'Dining Table', 'كرسي طعام':'Dining Chair', 'جزيرة مطبخ':'Kitchen Island', 'كرسي بار':'Bar Stool',
  'مرحاض معلق':'Wall-hung Toilet', 'وحدة حوض حمام':'Bathroom Vanity', 'كابينة شاور':'Glass Shower', 'حوض استحمام':'Bathtub',
  'شاشة تلفزيون 65 بوصة':'65" 4K TV', 'شاشة تلفزيون 55 بوصة':'55" 4K TV', 'مكيف سبليت':'Split AC', 'نبات داخلي':'Indoor Plant',
  'كامل المبنى':'Whole Building'
};

const nm = s => LANG === 'en' ? (NAMES_EN[s] ?? s) : s;

function applyStaticLang(){
  document.documentElement.lang = LANG === 'ar' ? 'ar' : 'en';
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
}

function setLang(l){
  if (!LANGS.includes(l) || l === LANG) return;
  LANG = l;
  try { localStorage.setItem(LANG_KEY, l); } catch(e){}
  applyStaticLang();
  buildLib();
  renderOpenings();
  renderDims();
  renderLabels();
  renderPanel();
  $('#tip').textContent = TIPS()[is3D() ? '3d' : '2d'];
  window.View3D?.relang();
}
$('#langSel').onclick = e => { const l = e.target.closest('[data-lang]')?.dataset.lang; if (l && l !== LANG) setLang(l); };

applyStaticLang(); syncFullscreen();"""

    content = re.sub(old_lang_engine_pattern, new_lang_engine, content)
    
    # 5. Materials in MATS
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
  wood:    {name:'خشب باركيه بلوط', price:320, sw:'#d8b88a'},
  walnut:  {name:'خشب باركيه جوز فاخر', price:380, sw:'#9b7250'},
  tile800: {name:'بورسلين 80×80', price:220, sw:'#ebe6dc'},
  tile600: {name:'سيراميك 60×60', price:160, sw:'#dfe3e1'},
  marble:  {name:'رخام كلكتا إيطالي فاخر', price:650, sw:'#f1eee8'},
  antislip:{name:'بلاط حجري مانع للانزلاق', price:140, sw:'#d3d8d4'},
  terrazzo:{name:'تيرازو مصقول', price:280, sw:'#e6dfd3'},
  carpet:  {name:'موكيت سجاد فاخر', price:200, sw:'#c9c3d3'},
};"""
    content = content.replace(old_mats, new_mats)
    
    # 6. Library in LIB (Furniture categories and items)
    old_lib_pattern = r"// 家具库：\[类型, 名称, 宽, 深, 颜色\]\s*const LIB = \[[\s\S]*?\];\s*const typeColor"
    new_lib = """// مكتبة الأثاث: [النوع, الاسم, العرض, العمق, اللون]
const LIB = [
  {cat:'غرف النوم', items:[
    ['bed','سرير ماستر 1.8m',1800,2000,'#c9d6df'],['bed','سرير 1.5m',1500,2000,'#d8c7dc'],['bed','سرير مفرد',1200,2000,'#e8d5b5'],
    ['crib','سرير أطفال',1250,700,'#efe3d0'],['nightstand','كومودينو',450,400,'#e8dccb'],['wardrobe','دولاب ملابس',2000,600,'#efe6d8'],
    ['wardrobe','خزانة صغيرة',1200,550,'#efe6d8'],['dresser','تسريحة ومرآة',1000,450,'#efe6d8'],['desk','مكتب دراسة',1200,600,'#e2cfb4'],
    ['chair','كرسي مكتب',450,480,'#cfc6b8'],['bookshelf','مكتبة رفوف كتب',800,300,'#e2cfb4'],['baycushion','جلسة شباك بانوراما',520,1800,'#e7dccd']]},
  {cat:'الصالون والمعيشة', items:[
    ['sofa','كنبة 3 مقاعد',2400,900,'#b7c4b0'],['sofa','كنبة ثنائية',1700,880,'#c3cbd6'],['cornersofa','كنبة زاوية عائلية',2800,1700,'#b7c4b0'],
    ['armchair','أريكة مفردة فوتيه',850,850,'#d6b99a'],['beanbag','بين باج مريح',800,800,'#e0b98f'],['coffeetable','طاولة رخام',1300,650,'#e8dccb'],
    ['sidetable','طاولة جانبية',500,500,'#d9c3a3'],['tvstand','وحدة تلفزيون جدارية',2400,400,'#e2cfb4'],['rug','سجادة صالون فاخرة',2400,1700,'#d9cbb8'],
    ['shoecab','خزانة أحذية',1000,350,'#efe6d8'],['shoecab','كونسول مدخل',1400,380,'#e6dccc'],['floorlamp','مصباح أرضي مودرن',450,450,'#3d3a34'],
    ['plant','نبات داخلي',500,500,'#a9c39b'],['plant','نبات زينة كبير',700,700,'#9dbb8c']]},
  {cat:'المطبخ وتناول الطعام', items:[
    ['table','طاولة طعام 4 كراسي',1400,800,'#e2cfb4'],['table','طاولة طعام 6 مقاعد',1800,900,'#d8c2a2'],['roundtable','طاولة طعام دائرية',1000,1000,'#e2cfb4'],
    ['chair','كرسي طعام',450,480,'#cfc6b8'],['island','جزيرة مطبخ رخامية',1800,900,'#e9e5de'],['barstool','كرسي بار مرتفع',420,420,'#6b5d4c'],
    ['counter','رخام مطبخ كاونتر',1600,600,'#e9e5de'],['stove','بوتاجاز غاز',750,450,'#dcdcdc'],['ksink','حوض غسيل',800,450,'#e1e6ea'],
    ['fridge','ثلاجة عائلية',700,700,'#dfe4e8'],['cabinet','بوفيه تقديم',1600,400,'#efe6d8']]},
  {cat:'الحمامات', items:[
    ['toilet','مرحاض معلق',400,700,'#ffffff'],['vanity','وحدة حوض حمام',800,500,'#eef1f3'],['vanity','وحدة حوض مزدوجة',1200,500,'#eef1f3'],
    ['shower','كابينة شاور',900,900,'#e4edf2'],['bathtub','حوض استحمام بانيو',1600,750,'#eef3f6'],['washer','غسالة ملابس',600,600,'#e6ebee'],
    ['waterheater','سخان مياه',800,450,'#f4f4f2'],['cabinet','خزانة حمام',1000,400,'#efe6d8']]},
  {cat:'الأجهزة المنزلية', items:[
    ['tv','شاشة تلفزيون 65 بوصة',1450,80,'#1d1d1f'],['tv','شاشة تلفزيون 55 بوصة',1230,80,'#1d1d1f'],['fridge','ثلاجة عائلية',910,700,'#c9ced3'],
    ['aircon','مكيف دولابي عمودي',500,380,'#f6f7f8'],['acwall','مكيف سبليت',900,250,'#f6f7f8'],['dishwasher','غسالة أطباق',600,600,'#dfe3e6'],
    ['cabinet','دولاب أفران مدمجة',600,600,'#2a2a2c'],['washer','مجفف ملابس',600,600,'#e6ebee'],['airpurifier','منقي هواء',350,350,'#ffffff']]},
  {cat:'المكتب والترفيه', items:[
    ['desk','طاولة مكتب عمل',1600,750,'#e2cfb4'],['chair','كرسي مكتب تنفيذي',600,600,'#3a3835'],['bookshelf','خزانة كتب جدارية',1200,350,'#e2cfb4'],
    ['piano','بيانو كلاسيكي',1500,650,'#1a1918'],['treadmill','جهاز سير رياضي',1800,800,'#2c2b2a'],['armchair','كرسي قراءة واسترخاء',800,850,'#c2b09a'],
    ['teatable','طاولة شاي وجلسة',1400,700,'#966b49'],['loungechair','كرسي استرخاء شيزلونج',700,1600,'#8f969b']]},
];
const typeColor"""
    content = re.sub(old_lib_pattern, new_lib, content)
    
    # 7. TIPS and Hints in Arabic
    tr_dict = {
        "'没有可撤销的操作'": "'لا توجد عمليات للتراجع عنها'",
        "'拖动旋转（Shift 自由角度）'": "'اسحب للتدوير (Shift لزاوية حرة)'",
        "'拖动调整尺寸'": "'اسحب لتعديل الحجم'",
        "'房间面积'": "'مساحات الغرف'",
        "'点击查看 / 更换地面'": "'اضغط للاستعراض وتغيير الأرضية'",
        "'套内使用面积'": "'إجمالي المساحة الصافية'",
        "'* 飘窗不计入使用面积；面积按墙体内净尺寸计算'": "'* المساحات محسوبة من الأوجه الداخلية الصافية للجدران'",
        "'地面材料估算'": "'حساب تكلفة وتوزيع الأرضيات'",
        "'含 5% 损耗'": "'شامل 5% نسبة هالك'",
        "'地面材料合计'": "'إجمالي تكلفة الأرضيات'",
        "'方案统计'": "'إحصائيات المخطط'",
        "'家具数量'": "'عدد قطع الأثاث'",
        "'拆除墙体'": "'الجدران المعدلة'",
        "'清除测量'": "'مسح القياسات'",
        "'清空布置'": "'إفراغ التأثيث'",
        "'旋转'": "'تدوير'",
        "'复制'": "'تكرار'",
        "'删除'": "'حذف'",
        "'属性'": "'الخصائص'",
        "'完成'": "'تم'",
        "'地面 / 属性'": "'الأرضية / الخصائص'",
        "'当前没有布置任何家具'": "'لا توجد أي قطع أثاث حالياً'",
        "'已清空布置，可点「撤销」恢复'": "'تم إفراغ الأثاث، يمكنك الضغط على «تراجع» للاستعادة'",
        "'房间'": "'الغرفة'",
        "'名称'": "'الاسم'",
        "'使用面积'": "'المساحة'",
        "'周长'": "'المحيط'",
        "'开间'": "'العرض'",
        "'进深'": "'العمق'",
        "'地面材料'": "'نوع الأرضية'",
        "'材料估价'": "'التكلفة التقديرية'",
        "'房间内家具'": "'الأثاث في الغرفة'",
        "'暂无'": "'لا يوجد'",
        "'← 返回总览'": "'← العودة للنظرة العامة'",
        "'家具属性'": "'خصائص الأثاث'",
        "'宽'": "'العرض'",
        "'深'": "'العمق'",
        "'中心'": "'المركز'",
        "'旋转 90°'": "'تدوير 90°'",
        "'置于顶层'": "'إحضار للأمام'",
        "'置于底层'": "'إرسال للخلف'",
        "'← 返回'": "'← عودة'",
        "'承重墙（黑色）不可拆除'": "'الجدران الحاملة الإنشائية لا يمكن إزالتها'",
        "'外墙属于建筑外围护结构，不建议拆除'": "'الجدران الخارجية واجهة معمارية لا يمكن إزالتها'",
        "'已恢复墙体'": "'تمت استعادة الجدار'",
        "'请拖到地面上'": "'يرجى الإسقاط داخل أرضية الغرفة'",
        "'户型装修方案'": "'مخطط-العمارة-السكنية'",
        "'3D 引擎仍在加载或加载失败（需要联网加载 three.js）'": "'جارِ تحميل محرك 3D...'",
        "'无法进入全屏'": "'تعذر تفعيل وضع ملء الشاشة'",
        "'退出全屏'": "'الخروج من ملء الشاشة'",
        "'全屏'": "'ملء الشاشة'",
        "'方案已导入'": "'تم استيراد المخطط بنجاح'",
        "'文件格式不正确'": "'صيغة الملف غير صحيحة'",
        "'恢复为默认设计方案？（可撤销）'": "'هل تريد استعادة التصميم الافتراضي؟ (يمكن التراجع)'",
        "'全屋'": "'كامل المبنى'",
        "'点或拖动家具库添加 · 单指拖动平移 · 双指缩放 · 选中家具后底部工具条可旋转 / 复制 / 删除'": "'اختر من مكتبة الأثاث للإضافة · اسحب بإصبع للتحريك · إصبعان للتكبير · اضغط الأثاث للتدوير أو الحذف'",
        "'单指旋转 · 双指缩放 / 平移 · 点家具或地面编辑 · 点门开关'": "'إصبع للتدوير 3D · إصبعان للتكبير/التحريك · انقر الأثاث لتعديله · انقر الأبواب لفتحها'",
        "'拖动左侧家具到平面图 · 滚轮缩放 · 拖动空白处平移 · T 切换 3D'": "'اسحب الأثاث من القائمة إلى المخطط · العجلة للتكبير · اسحب للتحريك · مفتاح T للتبديل ثلاثي الأبعاد'",
        "'3D 场景与平面方案实时同步 · 右侧面板修改会立即生效 · T 返回 2D'": "'المشهد ثلاثي الأبعاد متزامن فورياً مع المخطط · التعديلات تنطبق مباشرة · T للعودة 2D'",
        "'单指旋转 · 双指缩放 / 平移 · 点选家具后可拖动摆放 · 点门开关'": "'إصبع للتدوير · إصبعان للتقريب · انقر الأثاث لتعديله · انقر الأبواب لفتحها وإغلاقها'",
        "'左键旋转 · 右键平移 · 滚轮缩放 · 选中家具后拖动可摆放 · 点击门开关'": "'زر الماوس الأيسر للتدوير · الأيمن للتحريك · عجلة الماوس للتقريب · انقر الأبواب لفتحها'",
        "'左下摇杆移动 · 拖动画面转向 · 点门开关'": "'عصا التحكم باليسار للحركة · اسحب الشاشة للنظر · انقر الأبواب لفتحها'",
        "'WASD 移动 · 鼠标转向 · Shift 快走 · E 开关门 · Esc 暂停'": "'تحرك بمفاتيح WASD · حرك الماوس للنظر · Shift للسرعة · E لفتح الأبواب · Esc إيقاف مؤقت'",
        "'点击开始，从入户门进入'": "'اضغط للبدء، الدخول من ردهة الأبواب والمصعد'",
        "'左下摇杆移动 · 在画面上拖动转向'": "'استخدم عصا التحكم للحركة · اسحب في الشاشة لتغيير اتجاه النظر'",
        "'点门开关 · 点「退出漫游」回到鸟瞰'": "'انقر الأبواب لفتحها · اضغط «إنهاء الجولة» للعودة للمنظور العلوي'",
        "'<kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> 移动 · 鼠标转向 · <kbd>Shift</kbd> 快走'": "'<kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> للحركة · حرك الماوس للنظر · <kbd>Shift</kbd> للمشي السريع'",
        "'<kbd>E</kbd> 开关正前方的门 · <kbd>Esc</kbd> 暂停'": "'<kbd>E</kbd> أو النقر لفتح الأبواب أمامك · <kbd>Esc</kbd> إيقاف مؤقت'",
    }
    
    for zh, ar in tr_dict.items():
        content = content.replace(f"tr({zh},", f"tr({ar},")
        
    # Currency symbol: replace ¥ with ر.س (SAR)
    content = content.replace("¥${Math.round(c).toLocaleString()}", "${Math.round(c).toLocaleString()} ر.س")
    content = content.replace("¥${Math.round(cost).toLocaleString()}", "${Math.round(cost).toLocaleString()} ر.س")
    content = content.replace("¥${Math.round(area(r.poly)*MATS[st.mat].price*1.05).toLocaleString()}", "${Math.round(area(r.poly)*MATS[st.mat].price*1.05).toLocaleString()} ر.س")
    
    # Keyboard shortcut table
    old_kbd = """  <section><h3>${tr('键盘快捷键','Keyboard Shortcuts')}</h3><div class="kbd">
    <kbd>${tr('拖拽','Drag')}</kbd><span>${tr('左侧家具拖入平面图','Drag furniture onto the plan')}</span><kbd>V</kbd><span>${tr('选择 / 移动','Select / move')}</span><kbd>M</kbd><span>${tr('测量（Shift 水平/垂直）','Measure (Shift: horizontal/vertical)')}</span>
    <kbd>X</kbd><span>${tr('拆改非承重墙（黑色为承重墙）','Demolish non-bearing walls')}</span><kbd>R</kbd><span>${tr('旋转 90°（Shift 反向）','Rotate 90° (Shift: reverse)')}</span><kbd>${tr('方向键','Arrow keys')}</kbd><span>${tr('微调 10mm（Shift 100mm）','Nudge 10mm (Shift: 100mm)')}</span>
    <kbd>⌘/Ctrl D</kbd><span>${tr('复制','Duplicate')}</span><kbd>Delete</kbd><span>${tr('删除','Delete')}</span><kbd>⌘/Ctrl Z</kbd><span>${tr('撤销','Undo')}</span><kbd>T</kbd><span>${tr('切换 2D / 3D','Toggle 2D / 3D')}</span><kbd>F</kbd><span>${tr('适应窗口','Fit to window')}</span><kbd>Esc</kbd><span>${tr('取消选择','Deselect')}</span>
  </div></section>"""

    new_kbd = """  <section><h3>${tr('اختصارات لوحة المفاتيح','Keyboard Shortcuts')}</h3><div class="kbd">
    <kbd>${tr('سحب الأثاث','Drag')}</kbd><span>${tr('اسحب من المكتبة إلى المخطط','Drag furniture onto the plan')}</span><kbd>V</kbd><span>${tr('تحديد / تحريك','Select / move')}</span><kbd>M</kbd><span>${tr('قياس الأبعاد (Shift للأفقي/العمودي)','Measure (Shift: horizontal/vertical)')}</span>
    <kbd>X</kbd><span>${tr('تعديل الجدران (الأسود جدار حامل)','Demolish non-bearing walls')}</span><kbd>R</kbd><span>${tr('تدوير 90° (Shift للعكس)','Rotate 90° (Shift: reverse)')}</span><kbd>${tr('الأسهم','Arrow keys')}</kbd><span>${tr('تحريك دقيق 10mm (مع Shift 100mm)','Nudge 10mm (Shift: 100mm)')}</span>
    <kbd>Ctrl+D</kbd><span>${tr('تكرار العنصر','Duplicate')}</span><kbd>Delete</kbd><span>${tr('حذف','Delete')}</span><kbd>Ctrl+Z</kbd><span>${tr('تراجع','Undo')}</span><kbd>T</kbd><span>${tr('تبديل 2D / 3D','Toggle 2D / 3D')}</span><kbd>F</kbd><span>${tr('ملاءمة الشاشة','Fit to window')}</span><kbd>Esc</kbd><span>${tr('إلغاء التحديد','Deselect')}</span>
  </div></section>"""
    content = content.replace(old_kbd, new_kbd)
    
    return content

if __name__ == '__main__':
    base_dir = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d"
    house_path = os.path.join(base_dir, "house-3d.html")
    index_path = os.path.join(base_dir, "index.html")
    
    with open(house_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    localized = localize_content(content)
    
    with open(house_path, "w", encoding="utf-8") as f:
        f.write(localized)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(localized)
        
    print("Tajawal Arabic Localization successfully applied to house-3d.html and index.html!")
