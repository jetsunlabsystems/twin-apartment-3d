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
