// Electrical Layout Printable Sheet & Executive PDF Export
// Generates official engineering title block, symbol legend, and socket schedule

import { $, esc, fmt } from '../config.js';
import { tr, nm } from '../i18n.js';
import { ROOMS } from '../data/floorplan.js';
import { SOCKET_TYPES, SOCKET_HEIGHTS, calculateSocketSchedule } from '../data/electrical.js';
import { state } from '../2d/state.js';

export function openElectricalPrintSheet() {
  let modal = $('#elecPrintModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'elecPrintModal';
    modal.className = 'print-modal-backdrop';
    document.body.appendChild(modal);
  }

  const schedule = calculateSocketSchedule(state.sockets || [], ROOMS);
  const now = new Date();
  const dateStr = now.toLocaleDateString('ar-SA', { year: 'numeric', month: 'long', day: 'numeric' });
  const dateEn = now.toISOString().split('T')[0];

  // Clone active plan SVG for crisp vector rendering in the printable sheet
  const originalSvg = $('#plan');
  const svgClone = originalSvg ? originalSvg.cloneNode(true) : null;
  if (svgClone) {
    svgClone.removeAttribute('id');
    svgClone.setAttribute('class', 'print-sheet-svg');
    // Ensure clean print viewport
    svgClone.setAttribute('viewBox', '-1500 -1500 19000 32000');
    svgClone.setAttribute('width', '100%');
    svgClone.setAttribute('height', '100%');

    // Force visible layers for print
    const gFurn = svgClone.querySelector('#gFurn');
    if (gFurn) {
      gFurn.setAttribute('opacity', '0.28');
      gFurn.setAttribute('filter', 'grayscale(1)');
    }
    const gSockets = svgClone.querySelector('#gSockets');
    if (gSockets) gSockets.setAttribute('display', 'inline');

    const gSel = svgClone.querySelector('#gSel');
    if (gSel) gSel.innerHTML = '';
  }

  // Symbol legend items
  const legendRows = Object.values(SOCKET_TYPES).map(t => `
    <div class="legend-item">
      <span class="legend-sw" style="background:${t.color}">${t.icon}</span>
      <div class="legend-info">
        <b>${t.name.zh} <small>(${t.defaultHeight})</small></b>
        <span>${t.desc.zh}</span>
      </div>
    </div>
  `).join('');

  // Socket schedule table rows per room
  const scheduleRows = Object.entries(schedule.byRoom).map(([rName, counts]) => `
    <tr>
      <td>${esc(rName)}</td>
      <td class="c">${counts.duplex || '-'}</td>
      <td class="c">${counts.media || '-'}</td>
      <td class="c">${counts.appliance || '-'}</td>
      <td class="c">${counts.waterproof || '-'}</td>
      <td class="c">${counts.ac || '-'}</td>
      <td class="c">${counts.switch || '-'}</td>
      <td class="c bold">${counts.total}</td>
    </tr>
  `).join('');

  modal.innerHTML = `
    <div class="print-sheet-container">
      <div class="print-sheet-actions no-print">
        <div class="actions-left">
          <button class="btn primary" id="doPrintBtn">🖨️ ${tr('طباعة المخطط / حفظ PDF (Ctrl+P)', 'Print / Save as PDF')}</button>
          <button class="btn" id="dlPngBtn">📥 ${tr('تصدير كصورة عريضة PNG', 'Export as PNG')}</button>
        </div>
        <div class="actions-title">
          <span>⚡ ${tr('معاينة المخطط التنفيذي لشبكة الأفياش والمقابس', 'Executive Electrical Blueprint Sheet Preview')}</span>
        </div>
        <button class="btn close-btn" id="closePrintBtn">✕ ${tr('إغلاق', 'Close')}</button>
      </div>

      <div class="print-sheet-page" id="printSheetPage">
        <!-- Sheet Header & Title Block -->
        <header class="sheet-header">
          <div class="title-block-main">
            <h2>مخطط شبكة وتوزيع المقابس والأفياش الكهربائية</h2>
            <div class="en-sub">EXECUTIVE ELECTRICAL SOCKETS & OUTLETS LAYOUT PLAN</div>
            <div class="meta-tags">
              <span><b>المشروع:</b> عمارة سكنية فاخرة · الشقق المتطابقة</span>
              <span><b>كود المطابقة:</b> كود البناء السعودي SBC 401 & IEC</span>
              <span><b>المقياس:</b> 1:60 / 1:100 A3-A4</span>
              <span><b>التاريخ:</b> ${dateStr} (${dateEn})</span>
            </div>
          </div>
          <div class="sheet-stamp">
            <div class="stamp-box">
              <span class="stamp-title">المخطط التنفيذي المعتمد</span>
              <span class="stamp-id">DWG NO: E-101</span>
              <span class="stamp-status">APPROVED FOR EXECUTION</span>
            </div>
          </div>
        </header>

        <!-- Main Body: Floorplan Vector Blueprint + Legend & Schedule -->
        <div class="sheet-body">
          <div class="blueprint-canvas-box" id="blueprintCanvasBox">
            ${svgClone ? svgClone.outerHTML : '<div class="muted">Loading floorplan...</div>'}
          </div>

          <aside class="sheet-side-data">
            <!-- Legend Block -->
            <div class="sheet-card">
              <h4>مفتاح الرموز الهندسية (SYMBOLS LEGEND)</h4>
              <div class="legend-grid">
                ${legendRows}
              </div>
            </div>

            <!-- Schedule & Bill of Quantities -->
            <div class="sheet-card">
              <h4>جدول حصر المقابس بالمسطح (SCHEDULE OF SOCKETS)</h4>
              <table class="schedule-table">
                <thead>
                  <tr>
                    <th>الغرفة / الفراغ</th>
                    <th class="c" title="مزدوج 220V">مزدوج</th>
                    <th class="c" title="شاشة وبيانات">شاشة</th>
                    <th class="c" title="أجهزة ثقيلة">أجهزة</th>
                    <th class="c" title="مقاوم للماء">IP44</th>
                    <th class="c" title="تكييف">تكييف</th>
                    <th class="c" title="مفتاح إنارة">إنارة</th>
                    <th class="c">المجموع</th>
                  </tr>
                </thead>
                <tbody>
                  ${scheduleRows}
                </tbody>
                <tfoot>
                  <tr class="tfoot-row">
                    <td><b>الإجمالي الكلي</b></td>
                    <td class="c">${schedule.byType.duplex}</td>
                    <td class="c">${schedule.byType.media}</td>
                    <td class="c">${schedule.byType.appliance}</td>
                    <td class="c">${schedule.byType.waterproof}</td>
                    <td class="c">${schedule.byType.ac}</td>
                    <td class="c">${schedule.byType.switch}</td>
                    <td class="c total-val">${schedule.total} مقبس</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Engineering Notes -->
            <div class="sheet-card notes-card">
              <h4>ملاحظات هندسية وتنفيذية (GENERAL NOTES)</h4>
              <ol>
                <li>جميع الارتفاعات (AFF) محسوبة من منسوب تشطيب البلاط النهائي.</li>
                <li>تغذى مقابس المطبخ والغسالات والتكييف بدوائر كهربائية مستقلة من القاطع الرئيسي.</li>
                <li>المقابس في مناطق المغاسل والحمامات تكون مزودة بحماية قاطع التسريب الأرضي (ELCB / GFCI).</li>
                <li>تُركب مجاري وأنابيب الـ PVC المقاومة للحريق بقطر لا يقل عن 20 ملم داخل الجدران الخرسانية والبلوك.</li>
              </ol>
            </div>
          </aside>
        </div>

        <!-- Sheet Footer Bar -->
        <footer class="sheet-footer">
          <span>مكتب التصميم والاستشارات الهندسية المعمارية</span>
          <span>صفحة 1 من 1 · مخطط E-101</span>
          <span>تصميم وتنفيذ رقمي فائق الدقة · نظام FloorPlan 3D Engine</span>
        </footer>
      </div>
    </div>
  `;

  modal.classList.add('open');

  // Bind modal actions
  $('#closePrintBtn').onclick = () => modal.classList.remove('open');
  $('#doPrintBtn').onclick = () => window.print();
  $('#dlPngBtn').onclick = exportHighResSheetPNG;
}

/**
 * High Resolution PNG Sheet Exporter
 */
async function exportHighResSheetPNG() {
  const page = $('#printSheetPage');
  if (!page) return;

  try {
    const svgEl = page.querySelector('.print-sheet-svg');
    if (!svgEl) return;

    const xml = new XMLSerializer().serializeToString(svgEl);
    const svg64 = btoa(unescape(encodeURIComponent(xml)));
    const image64 = 'data:image/svg+xml;base64,' + svg64;

    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 2400;
      canvas.height = 1800;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      const a = document.createElement('a');
      a.download = `مخطط_الأفياش_الكهربائية_${Date.now()}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
    };
    img.src = image64;
  } catch (err) {
    console.error('Export PNG failed:', err);
    window.print();
  }
}
