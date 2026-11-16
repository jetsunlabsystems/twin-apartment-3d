
const CDP = require('chrome-remote-interface');

async function test() {
  const client = await CDP({ port: 9222 });
  const { Runtime } = client;
  await Runtime.enable();
  
  const res = await Runtime.evaluate({
    expression: \(() => {
      const labels = Array.from(document.querySelectorAll('.rlabel'));
      return labels.map(el => {
        const cs = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return {
          text: el.innerText.trim(),
          display: cs.display,
          opacity: cs.opacity,
          visibility: cs.visibility,
          zIndex: cs.zIndex,
          transform: cs.transform,
          rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
          parentTag: el.parentElement ? el.parentElement.tagName : null,
          parentDisplay: el.parentElement ? window.getComputedStyle(el.parentElement).display : null,
          parentVisibility: el.parentElement ? window.getComputedStyle(el.parentElement).visibility : null,
          parentOpacity: el.parentElement ? window.getComputedStyle(el.parentElement).opacity : null
        };
      });
    })()\,
    returnByValue: true
  });
  console.log(JSON.stringify(res.result.value, null, 2));
  await client.close();
}
test().catch(e => console.error(e));
