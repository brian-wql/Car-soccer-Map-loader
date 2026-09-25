# Car Soccer Map Loader
Load maps in Car-soccer !

# How to use
- Go to https://car-soccer.com
- Press Control + Shift + I (Or open Devtools)
- Paste-in the code to inject
```
(() => {
  // ---------- store the current map and intercept map loading ----------
  let currentMap = null;   // JSON text that will replace the map the game requests
  const isMap = o => o && typeof o === 'object' && 'checkpoints' in o && 'meshes' in o;

  const originalParse = JSON.parse;
  JSON.parse = function (t, r) {
    const out = originalParse.call(this, t, r);
    if (currentMap && isMap(out)) return originalParse.call(JSON, currentMap);
    return out;
  };

  const originalJson = Response.prototype.json;
  Response.prototype.json = async function () {
    const out = await originalJson.call(this);
    if (currentMap && isMap(out)) return originalParse.call(JSON, currentMap);
    return out;
  };

  // ---------- pick a file from disk ----------
  function pickFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async () => {
      if (!input.files[0]) return;
      const text = await input.files[0].text();
      currentMap = text;
      localStorage.setItem('csmap_last', text);
      console.log('Map selected and saved as last:', input.files[0].name);
      alert('Map "' + input.files[0].name + '" ready. Now open the map from the game menu.');
    };
    input.click();
  }

  // ---------- load the last saved map ----------
  function loadLast() {
    const text = localStorage.getItem('csmap_last');
    if (!text) {
      alert('No map saved yet. Pick one with option 1 first.');
      return;
    }
    currentMap = text;
    console.log('Last map loaded from browser storage.');
    alert('Last map ready. Now open the map from the game menu.');
  }

  // ---------- menu on the "5" key ----------
  window.addEventListener('keydown', (e) => {
    const target = e.target;
    const typing = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);
    if (typing || e.key !== '5') return;

    const choice = prompt('Map selector:\n1 = pick a file from disk\n2 = load the last map you picked');
    if (choice === '1') pickFile();
    else if (choice === '2') loadLast();
  });

  console.log('Ready! Press 5 at any time to open the map selector.');
})();
```
- Select the map in File Manager
- Join in the map: Dribbling challange remastered 1
- Enjoy!

Made by brian_wql (brian-wql)
