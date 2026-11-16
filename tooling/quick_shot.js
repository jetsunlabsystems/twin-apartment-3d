
const CDP = require('chrome-remote-interface');
const fs = require('fs');

async function shot() {
  const client = await CDP({ port: 9222 });
  const { Page, Runtime } = client;
  await Page.enable();
  await Runtime.enable();
  
  // Set view to 3D and isoWhole
  await Runtime.evaluate({
    expression: \(() => {
      if (window.View3D) {
        window.View3D.flyToIso();
      }
    })()  });
  
  await new Promise(r => setTimeout(r, 1500));
  const ss = await Page.captureScreenshot({ format: 'png' });
  fs.writeFileSync('C:/Users/owner/.gemini/antigravity/brain/45773e7d-8600-4233-94b0-4df6d96f96ed/qa_current_3d_state.png', Buffer.from(ss.data, 'base64'));
  console.log('Saved qa_current_3d_state.png');
  await client.close();
}
shot().catch(e => console.error(e));
