# -*- coding: utf-8 -*-
"""
Deep localization pass to replace all remaining Chinese strings in house-3d.html and index.html
with elegant Arabic (Tajawal font compatible).
"""
import re
import os

def deep_localize():
    base_dir = r"c:\Users\owner\Documents\Projects\SideProjects\floorplan-3d"
    targets = [os.path.join(base_dir, "house-3d.html"), os.path.join(base_dir, "index.html")]

    replacements = [
        # Title
        ('<title>户型装修设计</title>', '<title>عمارة سكنية فاخرة · شقتين متطابقتين</title>'),
        
        # Subtitle & Stats
        ("tr(`套内使用面积约 ${fmt(tot)} m² · 尺寸单位 mm · 原图比例 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`)",
         "tr(`المساحة الصافية الإجمالية ≈ ${fmt(tot)} م² · الأبعاد بالمليمتر (mm) · مقياس الرسم 1:60`, `Net floor area ≈ ${fmt(tot)} m² · Units: mm · Original scale 1:60`)"),

        ("tr('房间面积','Room Areas')", "tr('مساحات الغرف','Room Areas')"),
        ("tr('点击查看 / 更换地面','Click to view / change flooring')", "tr('اضغط للاستعراض وتغيير الأرضيات','Click to view / change flooring')"),
        ("tr('套内使用面积','Net floor area')", "tr('المساحة الصافية الإجمالية','Net floor area')"),
        ("tr('* 飘窗不计入使用面积；面积按墙体内净尺寸计算','* Bay windows are excluded; areas use net inner wall dimensions')",
         "tr('* المساحات محسوبة بدقة من الأوجه الداخلية الصافية للجدران','* Areas calculated using net inner wall dimensions')"),
        ("tr('地面材料估算','Flooring Estimate')", "tr('تقدير كميات وتكلفة الأرضيات','Flooring Estimate')"),
        ("tr('含 5% 损耗','incl. 5% waste')", "tr('شامل 5% نسبة هالك','incl. 5% waste')"),
        ("tr('地面材料合计','Flooring total')", "tr('إجمالي تكلفة الأرضيات','Flooring total')"),
        ("tr('方案统计','Plan Stats')", "tr('إحصائيات المخطط','Plan Stats')"),
        ("tr('家具数量','Furniture')", "tr('عدد قطع الأثاث','Furniture')"),
        ("tr('拆除墙体','Walls removed')", "tr('الجدران المعدلة','Walls removed')"),
        ("tr('清除测量','Clear measures')", "tr('مسح خطوط القياس','Clear measures')"),
        ("tr('清空布置','Clear layout')", "tr('إفراغ التأثيث','Clear layout')"),

        # Floating bar buttons
        ("tr('旋转','Rotate')", "tr('تدوير','Rotate')"),
        ("tr('复制','Duplicate')", "tr('نسخ','Duplicate')"),
        ("tr('删除','Delete')", "tr('حذف','Delete')"),
        ("tr('属性','Properties')", "tr('الخصائص','Properties')"),
        ("tr('完成','Done')", "tr('تم','Done')"),
        ("tr('地面 / 属性','Floor / Properties')", "tr('الأرضية / الخصائص','Floor / Properties')"),

        # Room Panel
        ("tr('房间','Room')", "tr('الغرفة','Room')"),
        ("tr('名称','Name')", "tr('اسم الغرفة','Name')"),
        ("tr('使用面积','Floor area')", "tr('المساحة الصافية','Floor area')"),
        ("tr('周长','Perimeter')", "tr('المحيط','Perimeter')"),
        ("tr('开间','Width')", "tr('العرض','Width')"),
        ("tr('进深','Depth')", "tr('العمق','Depth')"),
        ("tr('地面材料','Flooring')", "tr('نوع الأرضية','Flooring')"),
        ("tr('材料估价','Estimated cost')", "tr('تقدير التكلفة','Estimated cost')"),
        ("tr('房间内家具','Furniture in room')", "tr('الأثاث داخل الغرفة','Furniture in room')"),
        ("tr('件','items')", "tr('قطعة','items')"),
        ("tr('件家具','items')", "tr('قطعة أثاث','items')"),

        # Furniture properties
        ("tr('宽度','Width')", "tr('العرض (W)','Width')"),
        ("tr('深度','Depth')", "tr('العمق (D)','Depth')"),
        ("tr('旋转角度','Rotation')", "tr('زاوية الدوران','Rotation')"),
        ("tr('高度 / 离地','Height / elevation')", "tr('الارتفاع عن الأرض','Height / elevation')"),
        ("tr('主体颜色','Color')", "tr('اللون والخامة','Color')"),
        ("tr('重置尺寸','Reset size')", "tr('استعادة الأبعاد الأصلية','Reset size')"),

        # Tooltips & Handles
        ("tr('拖动旋转（Shift 锁定 45°）', 'Drag to rotate (Shift snaps 45°)')", "tr('اسحب للتدوير (Shift يقفل 45°)', 'Drag to rotate (Shift snaps 45°)')"),
        ("tr('拖动调整尺寸', 'Drag to resize')", "tr('اسحب لتعديل المقاس', 'Drag to resize')"),

        # Toasts
        ("tr('没有可撤销的操作', 'Nothing to undo')", "tr('لا توجد عمليات سابقة للتراجع عنها', 'Nothing to undo')"),
        ("tr('没有可重做的操作', 'Nothing to redo')", "tr('لا توجد عمليات للإعادة', 'Nothing to redo')"),
        ("tr('当前没有布置任何家具', 'There is no furniture to clear')", "tr('لا يوجد أثاث حالياً لإفراغه', 'There is no furniture to clear')"),
        ("tr('已清空布置，可点「撤销」恢复', 'Layout cleared — Undo to restore')", "tr('تم إفراغ التأثيث، يمكنك الضغط على «تراجع» للاستعادة', 'Layout cleared — Undo to restore')"),
        ("tr('已恢复为默认方案', 'Reset to default')", "tr('تمت استعادة التصميم الافتراضي للمبنى', 'Reset to default')"),

        # Help modal / Controls
        ("""${COARSE ? tr(`<section><h3>触屏操作</h3><div class="kbd">
    <kbd>单指拖动</kbd><span>空白处平移画面</span><kbd>双指</kbd><span>捏合缩放、拖动平移</span>
    <kbd>家具库</kbd><span>点一下放到画面中央，或按住向右拖到指定位置</span>
    <kbd>点家具</kbd><span>选中后拖动移动；拖顶部圆点旋转、右下方块改尺寸</span>
    <kbd>工具条</kbd><span>选中后底部可旋转 / 复制 / 删除</span>
    <kbd>قياس</kbd><span>按住拖出一条线，或依次点两点</span>
    <kbd>3D 漫游</kbd><span>左下摇杆移动，拖动屏幕转向，点门开关</span>
  </div></section>""",
         """${COARSE ? tr(`<section><h3>إيماءات شاشة اللمس</h3><div class="kbd">
    <kbd>سحب بإصبع واحد</kbd><span>تحريك الكاميرا والمشهد</span><kbd>إصبعين</kbd><span>تقريب / تصغير وتحريك</span>
    <kbd>مكتبة الأثاث</kbd><span>اضغط للإضافة في المركز، أو اسحب للموضع المطلوب</span>
    <kbd>تحديد قطعة</kbd><span>اسحب للتحريك؛ النقطة العلوية للتدوير والمربع لتعديل الحجم</span>
    <kbd>شريط الأدوات</kbd><span>أزرار سريعة للتدوير والنسخ والحذف</span>
    <kbd>أداة القياس</kbd><span>اسحب لرسم خط قياس أو انقر نقطتين</span>
    <kbd>جولة 3D</kbd><span>عصا التحكم السفلية للحركة، اسحب للنظر حولك، انقر على الأبواب لفتحها</span>
  </div></section>"""),

        ("""${tr(`<section><h3>键盘快捷键</h3><div class="kbd">
    <kbd>拖拽</kbd><span>左侧家具拖入平面图</span><kbd>V</kbd><span>选择 / 移动</span><kbd>M</kbd><span>测量（Shift 水平/垂直）</span>
    <kbd>X</kbd><span>拆改非承重墙（黑色为承重墙）</span><kbd>R</kbd><span>旋转 90°（Shift 反向）</span><kbd>方向键</kbd><span>微调 10mm（Shift 100mm）</span>
    <kbd>⌘/Ctrl D</kbd><span>复制</span><kbd>Delete</kbd><span>删除</span><kbd>⌘/Ctrl Z</kbd><span>تراجع</span><kbd>T</kbd><span>切换 2D / 3D</span><kbd>F</kbd><span>适应窗口</span><kbd>Esc</kbd><span>取消选择</span>
  </div></section>""",
         """${tr(`<section><h3>اختصارات لوحة المفاتيح</h3><div class="kbd">
    <kbd>سحب وإفلات</kbd><span>سحب الأثاث من القائمة إلى المخطط</span><kbd>V</kbd><span>تحديد / تحريك</span><kbd>M</kbd><span>قياس الأبعاد</span>
    <kbd>X</kbd><span>تعديل الجدران غير الإنشائية</span><kbd>R</kbd><span>تدوير 90 درجة</span><kbd>الأسهم</kbd><span>تحريك دقيق 10 مم</span>
    <kbd>Ctrl + D</kbd><span>تكرار ونسخ</span><kbd>Delete</kbd><span>حذف القطعة</span><kbd>Ctrl + Z</kbd><span>تراجع</span><kbd>T</kbd><span>تبديل 2D / 3D</span><kbd>F</kbd><span>ملاءمة الشاشة</span><kbd>Esc</kbd><span>إلغاء التحديد</span>
  </div></section>"""),

        # Currency
        ("¥${m.price}/m²", "${m.price} ر.س / م²"),
        ("¥${m.price}", "${m.price} ر.س"),
        ("¥${Math.round(cost).toLocaleString()}", "${Math.round(cost).toLocaleString()} ر.س"),
        ("¥${Math.round(c).toLocaleString()}", "${Math.round(c).toLocaleString()} ر.س"),
        ("¥${Math.round(a*MATS[st.mat].price*1.05).toLocaleString()}", "${Math.round(a*MATS[st.mat].price*1.05).toLocaleString()} ر.س"),
        
        # Room list header & walk mode
        ('data-en="Whole home">全部<', 'data-en="Whole home">كامل المبنى<'),
        ('title="全屏 (Shift+F)"', 'title="ملء الشاشة (Shift+F)"'),
    ]

    for p in targets:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()

        for old, new in replacements:
            content = content.replace(old, new)

        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Deep localized {os.path.basename(p)}")

if __name__ == '__main__':
    deep_localize()
