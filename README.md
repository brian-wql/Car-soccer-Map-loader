# Car Soccer Map Loader
Load maps in Car-soccer !

# How to use
- Go to https://car-soccer.com
- Press Control + Shift + I (Or open Devtools)
- Paste-in the code
```
(async () => {
  const arq = await new Promise(res => {
    const i = document.createElement('input');
    i.type = 'file';
    i.accept = '.json';
    i.onchange = () => res(i.files[0]);
    i.click();
  });
  const texto = await arq.text();
  const novo = JSON.parse(texto);
  const ehMapa = o => o && typeof o === 'object' && 'ballGoals' in o && 'meshes' in o;

  // 1) JSON.parse
  const parseOrig = JSON.parse;
  JSON.parse = function (t, r) {
    const out = parseOrig.call(this, t, r);
    if (ehMapa(out)) { console.log('JSON.parse: mapa Switched!'); return structuredClone(novo); }
    return out;
  };

  // 2) response.json()
  const jsonOrig = Response.prototype.json;
  Response.prototype.json = async function () {
    const out = await jsonOrig.call(this);
    if (ehMapa(out)) { console.log('response.json: map Switched!', this.url); return structuredClone(novo); }
    return out;
  };

  // 3) só espiar as requisições
  const fetchOrig = window.fetch;
  window.fetch = function (input, init) {
    console.log('fetch:', String(input?.url ?? input));
    return fetchOrig.call(window, input, init);
  };
  const open = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (m, url) {
    console.log('XHR:', url);
    return open.apply(this, arguments);
  };

  console.log('Ready! Select the map Dribbling challange remastered 1.');
})();
```
- Select the map in File Manager
- Join in the map: Dribbling challange remastered 1
- Enjoy!

Made by brian_wql (brian-wql)
(im sorry for the code being PT-BR, im Brazilian btw)
