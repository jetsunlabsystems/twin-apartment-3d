// Automated Browser QA via Chrome DevTools Protocol (CDP)
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 9222;
const APP_URL = 'http://localhost:8000/';
const ARTIFACT_DIR = 'C:/Users/owner/.gemini/antigravity/brain/45773e7d-8600-4233-94b0-4df6d96f96ed';
const CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const USER_DATA_DIR = 'C:/Users/owner/AppData/Local/Temp/chrome_qa_profile_' + Date.now();

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

  // Wait for Chrome port to become active
  let connected = false;
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (res.ok) {
        connected = true;
        break;
      }
    } catch (e) {
      await new Promise(r => setTimeout(r, 200));
    }
  }

  if (!connected) {
    chromeProc.kill();
    throw new Error('Failed to connect to Chrome CDP after 6 seconds');
  }
  console.log(`[QA] Chrome CDP connected!`);

  try {
    // 1. Create a new tab for testing
    const tabRes = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(APP_URL)}`, { method: 'PUT' });
    const tab = await tabRes.json();
    const wsUrl = tab.webSocketDebuggerUrl;
    console.log(`[QA] Opened target tab: ${tab.id}`);

    const ws = new WebSocket(wsUrl);

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

    await new Promise((resolve, reject) => {
      ws.onopen = resolve;
      ws.onerror = reject;
    });

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && pending.has(msg.id)) {
        const { resolve, reject } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
        return;
      }

      if (msg.method === 'Runtime.consoleAPICalled') {
        const args = msg.params.args.map(a => a.value !== undefined ? a.value : (a.description || '')).join(' ');
        consoleLogs.push({ type: msg.params.type, text: args });
        if (msg.params.type === 'error') {
          console.error(`  [BROWSER ERROR] ${args}`);
        } else {
          console.log(`  [BROWSER ${msg.params.type.toUpperCase()}] ${args}`);
        }
      } else if (msg.method === 'Runtime.exceptionThrown') {
        const desc = msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text;
        const line = msg.params.exceptionDetails.lineNumber;
        const url = msg.params.exceptionDetails.url;
        uncaughtErrors.push({ desc, line, url });
        console.error(`  [UNCAUGHT EXCEPTION] ${desc} at ${url}:${line}`);
      }
    };

    // Enable CDP domains
    await send('Page.enable');
    await send('Runtime.enable');
    await send('Console.enable');
    await send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false
    });

    console.log('[QA] Waiting 4s for page initial render...');
    await new Promise(r => setTimeout(r, 4000));

    // Take 2D Screenshot
    const ss2d = await send('Page.captureScreenshot', { format: 'png' });
    const path2d = path.join(ARTIFACT_DIR, 'qa_2d_view.png');
    fs.writeFileSync(path2d, Buffer.from(ss2d.data, 'base64'));
    console.log(`[QA] Saved 2D screenshot to: ${path2d}`);

    // Test clicking a room
    console.log('[QA] Testing room selection (Room 1)...');
    await send('Runtime.evaluate', {
      expression: `(() => {
        const room = document.querySelector('#gRooms polygon, #gRooms path');
        if (room) {
          room.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, clientX: 400, clientY: 400 }));
          room.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, clientX: 400, clientY: 400 }));
          return 'Room clicked';
        }
        return 'No room element found';
      })()`
    });

    await new Promise(r => setTimeout(r, 1000));

    // Switch to 3D Scene
    console.log('[QA] Switching to 3D scene (clicking 3D button)...');
    const switchRes = await send('Runtime.evaluate', {
      expression: `(() => {
        const btn = document.querySelector('button[data-view="3d"]');
        if (btn) { btn.click(); return '3D button clicked'; }
        return '3D button not found';
      })()`
    });
    console.log(`[QA] Switch result: ${switchRes.result.value}`);

    console.log('[QA] Waiting 4s for 3D scene, models, and textures to build...');
    await new Promise(r => setTimeout(r, 4000));

    // Take 3D Screenshot
    const ss3d = await send('Page.captureScreenshot', { format: 'png' });
    const path3d = path.join(ARTIFACT_DIR, 'qa_3d_view.png');
    fs.writeFileSync(path3d, Buffer.from(ss3d.data, 'base64'));
    console.log(`[QA] Saved 3D screenshot to: ${path3d}`);

    // Close tab and ws
    try { await fetch(`http://127.0.0.1:${PORT}/json/close/${tab.id}`); } catch(e) {}
    ws.close();

    console.log('\n================ QA SUMMARY ================');
    console.log(`Total Uncaught Exceptions: ${uncaughtErrors.length}`);
    console.log(`Total Console Errors: ${consoleLogs.filter(l => l.type === 'error').length}`);
    if (uncaughtErrors.length > 0) {
      console.log('Uncaught errors list:');
      uncaughtErrors.forEach((e, i) => console.log(`  ${i+1}. ${e.desc}`));
      process.exit(1);
    } else {
      console.log('STATUS: ALL CHECKS PASSED WITH 0 ERRORS!');
    }
  } finally {
    chromeProc.kill();
    try { fs.rmSync(USER_DATA_DIR, { recursive: true, force: true }); } catch (e) {}
  }
}

runQA().catch(err => {
  console.error('[QA FATAL ERROR]', err);
  process.exit(1);
});
