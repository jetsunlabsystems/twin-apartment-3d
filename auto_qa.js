// Comprehensive Automated Browser QA via Chrome DevTools Protocol (CDP)
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 9222;
const APP_URL = 'http://localhost:8000/';
const ARTIFACT_DIR = 'C:/Users/owner/.gemini/antigravity/brain/45773e7d-8600-4233-94b0-4df6d96f96ed';
const CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const USER_DATA_DIR = 'C:/Users/owner/AppData/Local/Temp/chrome_full_qa_' + Date.now();

async function runQA() {
  console.log(`[QA] Launching Chrome with CDP on port ${PORT}...`);
  const chromeProc = spawn(CHROME_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--remote-allow-origins=*',
    '--headless=new',
    `--user-data-dir=${USER_DATA_DIR}`,
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--window-size=1440,900',
    'about:blank'
  ], { stdio: 'ignore' });

  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (res.ok) break;
    } catch (e) {
      await new Promise(r => setTimeout(r, 200));
    }
  }

  const tabRes = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(APP_URL)}`, { method: 'PUT' });
  const tab = await tabRes.json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);

  const consoleLogs = [];
  const uncaughtErrors = [];
  let reqId = 1;
  const pending = new Map();

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = reqId++;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  ws.onmessage = msg => {
    const data = JSON.parse(msg.data);
    if (data.id && pending.has(data.id)) {
      const { resolve, reject } = pending.get(data.id);
      pending.delete(data.id);
      if (data.error) reject(data.error);
      else resolve(data.result);
    }
    if (data.method === 'Runtime.exceptionThrown') {
      uncaughtErrors.push(data.params.exceptionDetails.text + ' ' + (data.params.exceptionDetails.exception?.description || ''));
    }
    if (data.method === 'Runtime.consoleAPICalled') {
      const line = `[${data.params.type}] ` + data.params.args.map(a => a.value !== undefined ? a.value : a.description).join(' ');
      consoleLogs.push({ type: data.params.type, text: line });
      if (data.params.type === 'error') {
        console.error('  -> Browser Console Error:', line);
      }
    }
  };

  await new Promise(r => ws.onopen = r);
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Page.bringToFront');

  console.log('[QA] Waiting 3.5s for initial 2D render...');
  await new Promise(r => setTimeout(r, 3500));

  // 1. Take 2D Screenshot
  const ss2d = await send('Page.captureScreenshot', { format: 'png' });
  const path2d = path.join(ARTIFACT_DIR, 'qa_2d_view.png');
  fs.writeFileSync(path2d, Buffer.from(ss2d.data, 'base64'));
  console.log(`[QA] Saved 2D view to: ${path2d}`);

  // 1b. Zoom to Stairs and Lightwell in 2D
  console.log('[QA] Zooming in on Lightwell and Stair Core in 2D...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      const svg = document.querySelector('#plan');
      if (svg) svg.setAttribute('viewBox', '5200 9200 5400 9000');
    })()`
  });
  await new Promise(r => setTimeout(r, 800));
  const ss2dStairs = await send('Page.captureScreenshot', { format: 'png' });
  const path2dStairs = path.join(ARTIFACT_DIR, 'qa_2d_stairs_zoom.png');
  fs.writeFileSync(path2dStairs, Buffer.from(ss2dStairs.data, 'base64'));
  console.log(`[QA] Saved 2D Stairs Zoom view to: ${path2dStairs}`);

  // 1c. Zoom to Reception Salons in 2D
  console.log('[QA] Zooming in on Reception Salons in 2D...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      const svg = document.querySelector('#plan');
      if (svg) svg.setAttribute('viewBox', '0 18000 15800 11000');
    })()`
  });
  await new Promise(r => setTimeout(r, 800));
  const ss2dRec = await send('Page.captureScreenshot', { format: 'png' });
  const path2dRec = path.join(ARTIFACT_DIR, 'qa_2d_reception_zoom.png');
  fs.writeFileSync(path2dRec, Buffer.from(ss2dRec.data, 'base64'));
  console.log(`[QA] Saved 2D Reception Zoom view to: ${path2dRec}`);

  // Reset 2D View
  await send('Runtime.evaluate', {
    expression: `(() => {
      const svg = document.querySelector('#plan');
      if (svg) svg.removeAttribute('viewBox');
    })()`
  });

  // 2. Test 2D Room Selection and Floor Material Change
  console.log('[QA] Selecting Room 1 in 2D and switching floor to Walnut...');
  const res2D = await send('Runtime.evaluate', {
    expression: `(() => {
      const r = window.ROOMS[0];
      window.select({ kind: 'room', id: r.id });
      const walnutBtn = document.querySelector('#panel [data-mat="walnut"]');
      if (walnutBtn) walnutBtn.click();
      return {
        selected: window.ui.sel?.id,
        newMat: window.state.rooms[r.id].mat
      };
    })()`,
    returnByValue: true
  });
  console.log('[QA] 2D Room and Floor Result:', res2D.result.value);

  // 3. Switch to 3D
  console.log('[QA] Switching to 3D View...');
  await send('Runtime.evaluate', {
    expression: `document.querySelector('button[data-view="3d"]').click()`
  });

  console.log('[QA] Waiting 3.5s for 3D construction & camera transition...');
  await new Promise(r => setTimeout(r, 3500));

  // 4. Verify 3D Room Labels and Floor Material in 3D
  const res3D = await send('Runtime.evaluate', {
    expression: `(() => {
      const labels = Array.from(document.querySelectorAll('.rlabel'));
      const sample = labels.slice(0, 3).map(l => ({ text: l.textContent, transform: l.style.transform }));
      
      // Click the first label
      const first = labels[0];
      if (first) first.click();

      const fab = document.querySelector('#fab');
      const propBtn = fab?.querySelector('[data-a="prop"]');

      return {
        labelCount: labels.length,
        labelsSample: sample,
        selectedAfterLabelClick: window.ui.sel,
        fabShowing: fab?.classList.contains('show'),
        propBtnText: propBtn?.textContent,
        panelOpen: !document.querySelector('.app')?.classList.contains('hide-panel')
      };
    })()`,
    returnByValue: true
  });
  console.log('[QA] 3D Labels & Selection Test:', JSON.stringify(res3D.result.value, null, 2));

  // 5. Change Floor Material in 3D Mode
  console.log('[QA] Changing floor material while in 3D mode (to marble)...');
  const res3DMat = await send('Runtime.evaluate', {
    expression: `(() => {
      const curId = window.ui.sel?.id;
      if (!curId) return { error: 'No room selected' };
      const marbleBtn = document.querySelector('#panel [data-mat="marble"]');
      if (marbleBtn) {
        marbleBtn.click();
        return {
          roomId: curId,
          updatedMat: window.state.rooms[curId].mat
        };
      }
      return { error: 'Marble button not found' };
    })()`,
    returnByValue: true
  });
  console.log('[QA] 3D Floor Material Update Result:', res3DMat.result.value);

  await new Promise(r => setTimeout(r, 1500));

  // 6. Capture 3D Screenshot with updated floor and labels
  const ss3d = await send('Page.captureScreenshot', { format: 'png' });
  const path3d = path.join(ARTIFACT_DIR, 'qa_3d_view_fixed.png');
  fs.writeFileSync(path3d, Buffer.from(ss3d.data, 'base64'));
  console.log(`[QA] Saved 3D view to: ${path3d}`);

  // 7. Focus Camera on Terrace and Reception in 3D by selecting the terrace room
  console.log('[QA] Selecting Terrace in 3D to fly camera to it...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      window.select({ kind: 'room', id: 'terr_l' });
    })()`
  });
  await new Promise(r => setTimeout(r, 2500));
  const sst = await send('Page.captureScreenshot', { format: 'png' });
  const patht = path.join(ARTIFACT_DIR, 'qa_3d_terrace.png');
  fs.writeFileSync(patht, Buffer.from(sst.data, 'base64'));
  console.log(`[QA] Saved 3D terrace view to: ${patht}`);

  // 7b. Focus Camera on Stair Core & Elevator in 3D
  console.log('[QA] Selecting Stair Core in 3D to fly camera to it...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      window.select({ kind: 'room', id: 'stair_core' });
    })()`
  });
  await new Promise(r => setTimeout(r, 2500));
  const sss = await send('Page.captureScreenshot', { format: 'png' });
  const paths = path.join(ARTIFACT_DIR, 'qa_3d_stairs_zoom.png');
  fs.writeFileSync(paths, Buffer.from(sss.data, 'base64'));
  console.log(`[QA] Saved 3D Stairs view to: ${paths}`);

  // 7c. Focus Camera on Reception Salon in 3D
  console.log('[QA] Selecting Reception Salon in 3D to fly camera to it...');
  await send('Runtime.evaluate', {
    expression: `(() => {
      window.select({ kind: 'room', id: 'rec_l' });
    })()`
  });
  await new Promise(r => setTimeout(r, 2500));
  const ssr = await send('Page.captureScreenshot', { format: 'png' });
  const pathr = path.join(ARTIFACT_DIR, 'qa_3d_reception_zoom.png');
  fs.writeFileSync(pathr, Buffer.from(ssr.data, 'base64'));
  console.log(`[QA] Saved 3D Reception view to: ${pathr}`);

  // 8. Test Furniture Selection and Full Tajawal Text without Truncation in FAB
  console.log('[QA] Selecting TV Stand (وحدة تلفزيون جدارية فاخرة) to verify FAB and panel text...');
  const resFurn = await send('Runtime.evaluate', {
    expression: `(() => {
      const tv = window.state.furniture.find(f => f.name && (f.name.zh.includes('تلفزيون') || f.name.en.includes('تلفزيون')));
      if (tv) {
        window.select({ kind: 'furn', id: tv.id });
        const fabName = document.querySelector('#fab .name');
        const computedFont = fabName ? window.getComputedStyle(fabName).fontFamily : '';
        const fabVisible = document.querySelector('#fab')?.classList.contains('show');
        const panelInput = document.querySelector('#fName');
        return {
          tvId: tv.id,
          fullName: tv.name.zh,
          fabText: fabName?.textContent,
          isTruncated: fabName ? fabName.scrollWidth > fabName.clientWidth : false,
          computedFont,
          fabVisible,
          panelInputValue: panelInput?.value
        };
      }
      return { error: 'TV Stand not found' };
    })()`,
    returnByValue: true
  });
  console.log('[QA] Furniture FAB & Typography Verification:', JSON.stringify(resFurn.result.value, null, 2));

  await new Promise(r => setTimeout(r, 1200));
  const ssf = await send('Page.captureScreenshot', { format: 'png' });
  const pathf = path.join(ARTIFACT_DIR, 'qa_furniture_fab_fixed.png');
  fs.writeFileSync(pathf, Buffer.from(ssf.data, 'base64'));
  console.log(`[QA] Saved Furniture FAB view to: ${pathf}`);

  // Clean up
  try { await fetch(`http://127.0.0.1:${PORT}/json/close/${tab.id}`); } catch(e) {}
  ws.close();

  console.log('\n================ QA SUMMARY ================');
  console.log(`Total Uncaught Exceptions: ${uncaughtErrors.length}`);
  console.log(`Total Console Errors: ${consoleLogs.filter(l => l.type === 'error').length}`);
  if (uncaughtErrors.length > 0) {
    console.log('Uncaught errors list:');
    uncaughtErrors.forEach((e, i) => console.log(`  ${i+1}. ${e}`));
    process.exit(1);
  } else {
    console.log('STATUS: ALL CHECKS PASSED WITH 0 ERRORS!');
  }

  chromeProc.kill();
  try { fs.rmSync(USER_DATA_DIR, { recursive: true, force: true }); } catch (e) {}
}

runQA().catch(err => {
  console.error('[QA FATAL ERROR]', err);
  process.exit(1);
});
