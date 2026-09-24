# Car Soccer Map Loader
Load maps in Car-soccer !

# How to use
- Go to https://car-soccer.com
- Press Control + Shift + I (Or open Devtools)
- Paste-in the code to inject
```
(async () => {
  const file = await new Promise(resolve => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = () => resolve(input.files[0]);
    input.click();
  });

  const text = await file.text();
  const newMap = JSON.parse(text);

  const isMap = obj =>
    obj &&
    typeof obj === 'object' &&
    'ballGoals' in obj &&
    'meshes' in obj;

  // 1) JSON.parse
  const originalParse = JSON.parse;

  JSON.parse = function (text, reviver) {
    const output = originalParse.call(this, text, reviver);

    if (isMap(output)) {
      console.log('JSON.parse: map replaced!');
      return structuredClone(newMap);
    }

    return output;
  };

  // 2) response.json()
  const originalJson = Response.prototype.json;

  Response.prototype.json = async function () {
    const output = await originalJson.call(this);

    if (isMap(output)) {
      console.log(
        'response.json: map replaced!',
        this.url
      );

      return structuredClone(newMap);
    }

    return output;
  };

  // 3) Only monitor requests
  const originalFetch = window.fetch;

  window.fetch = function (input, init) {
    console.log(
      'fetch:',
      String(input?.url ?? input)
    );

    return originalFetch.call(
      window,
      input,
      init
    );
  };

  const originalOpen = XMLHttpRequest.prototype.open;

  XMLHttpRequest.prototype.open = function (method, url) {
    console.log('XHR:', url);

    return originalOpen.apply(
      this,
      arguments
    );
  };

  console.log(
    'Ready! Now select the map in the game without reloading the page.'
  );
})();
```
- Select the map in File Manager
- Join in the map: Dribbling challange remastered 1
- Enjoy!

Made by brian_wql (brian-wql)
