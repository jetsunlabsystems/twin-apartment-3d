// Main Application Bootstrap & Module Integrator
import { $, COARSE } from './config.js';
import { LANG, setLang, applyStaticLang, TIPS } from './i18n.js';
import { state, ui, onStateChange } from './2d/state.js';
import { buildDefs, renderOpenings, renderDims, renderAll } from './2d/renderer.js';
import { fitView, applyView, select } from './2d/interactions.js';
import { buildLib, initToolbar, syncFullscreen, updateHeader, viewMode, is3D } from './ui/toolbar.js';
import { renderPanel, syncPaneBtns } from './ui/panels.js';
import { init3D, View3D } from './3d/scene.js';

// 1. Initial UI & Language Setup
applyStaticLang();
syncFullscreen();
syncPaneBtns();
buildDefs();
buildLib();
initToolbar();
renderOpenings();
renderDims();
renderPanel();
updateHeader();

// 2. Initial View Framing & 2D Render
fitView();
renderAll();

if ($('#tip') && typeof TIPS === 'function') {
  $('#tip').textContent = TIPS()['2d'] || '';
}

// 3. Initialize 3D Engine
if (typeof init3D === 'function') {
  init3D();
}

// 4. Hook State Changes
onStateChange(() => {
  renderAll();
  renderPanel();
  updateHeader();
  if (is3D() && window.View3D?.sync) {
    window.View3D.sync();
  }
});

console.log("Twin Apartment 3D Modular App Loaded Successfully.");
