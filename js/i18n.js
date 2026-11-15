// Localization Engine & Tajawal Arabic / English Text Dictionaries
import { COARSE, LANG_KEY } from './config.js';

export const LANG_MAP = {
  zh: 'العربية',
  en: 'English'
};

export let LANG = (() => {
  try {
    const l = localStorage.getItem(LANG_KEY);
    return (l === 'en' || l === 'zh') ? l : 'zh';
  } catch (e) {
    return 'zh';
  }
})();

export function tr(arText, enText) {
  return LANG === 'en' ? (enText || arText) : arText;
}

export function nm(o) {
  if (!o) return '';
  if (typeof o === 'string') return o;
  return LANG === 'en' ? (o.en || o.zh || '') : (o.zh || o.en || '');
}

export function setLang(l, onLangChange) {
  LANG = (l === 'zht' || l === 'en') ? 'en' : 'zh';
  try {
    localStorage.setItem(LANG_KEY, LANG);
  } catch (e) {}
  document.documentElement.lang = LANG === 'zh' ? 'ar' : 'en';
  document.documentElement.dir = LANG === 'zh' ? 'rtl' : 'ltr';
  applyStaticLang();
  if (typeof onLangChange === 'function') {
    onLangChange(LANG);
  }
}

export function applyStaticLang() {
  document.querySelectorAll('[data-en]').forEach(el => {
    if (!el.dataset.zh) el.dataset.zh = el.textContent;
    el.textContent = LANG === 'en' ? el.dataset.en : el.dataset.zh;
  });
  document.querySelectorAll('#langSel .btn').forEach(b => {
    const l = b.dataset.lang;
    const on = (LANG === 'zh' && l === 'zh') || (LANG === 'en' && (l === 'en' || l === 'zht'));
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
}

export const TIPS = () => COARSE
  ? {
      '2d': tr('اضغط أو اسحب من مكتبة الأثاث · سحب بإصبع للتحريك · إصبعين للتقريب · شريط الأدوات بالأسفل للتدوير والنسخ والحذف',
               'Tap or drag from the library · 1 finger pans · pinch zooms · bottom bar rotates / duplicates / deletes'),
      '3d': tr('سحب بإصبع للدوران · إصبعين للتكبير/التحريك · اضغط على الأثاث أو الأرضية للتعديل · اضغط على الأبواب لفتحها',
               '1 finger orbits · 2 fingers zoom / pan · tap furniture or floor to edit · tap doors to open')
    }
  : {
      '2d': tr('اسحب الأثاث من القائمة اليسرى إلى المخطط · العجلة للتكبير · اسحب بالفأرة للتحريك · مفتاح T للتبديل إلى 3D',
               'Drag furniture onto the plan · scroll to zoom · drag empty space to pan · T toggles 3D'),
      '3d': tr('السحب بالأيسر للدوران · السحب بالأيمن للتحريك · العجلة للتقريب · اضغط على الأثاث للسحب والتعديل · اضغط على الأبواب لفتحها',
               'Left-drag orbits · right-drag pans · scroll zooms · select furniture to drag it · click doors to open')
    };
