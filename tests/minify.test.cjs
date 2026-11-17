const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');
const { minifySource, minifySite } = require('../scripts/minify.cjs');

test('HTML compression preserves text spacing, code, form values, and JSON-LD', async () => {
  const pre = '  const answer = 42;\n    answer + 1;\n';
  const value = '  Keep  these spaces\n and this line\n';
  const data = { '@context': 'https://schema.org', name: 'A  B', description: 'Quotes " and <tags>' };
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  const source = `<!DOCTYPE html><html><head>
    <style>p { color: red; margin: 0px; }</style>
    <script type="application/ld+json">${json}</script>
    </head><body><!-- remove -->
    <p>Hello <em>wide</em> world</p><pre>${pre}</pre><textarea>${value}</textarea>
    <script>window.result = 40 + 2;</script></body></html>`;
  const output = await minifySource('page.html', source);
  assert.ok(output.length < source.length);
  assert.ok(output.includes('<p>Hello <em>wide</em> world</p>'));
  assert.ok(output.includes(`<pre>${pre}</pre>`));
  assert.ok(output.includes(`<textarea>${value}</textarea>`));
  assert.ok(!output.includes('<!-- remove -->'));
  assert.deepEqual(JSON.parse(output.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1]), data);
  const context = { window: {} };
  runInNewContext(output.match(/<script>(.*?)<\/script>/s)[1], context);
  assert.equal(context.window.result, 42);
});

test('Build minifies only generated HTML/CSS/JS and reports invalid JS', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'relcfp-minify-'));
  try {
    const css = 'p { background: url(../image.png); color: red; }\n';
    const js = '/* comment */\nwindow.result = 40 + 2;\n';
    mkdirSync(join(directory, 'assets'));
    mkdirSync(join(directory, 'pagefind'));
    writeFileSync(join(directory, 'assets/main.css'), css);
    writeFileSync(join(directory, 'assets/posts.js'), js);
    writeFileSync(join(directory, 'index.html'), '<html>\n<body>\n<p>Hello</p>\n</body>\n</html>');
    writeFileSync(join(directory, 'pagefind/pagefind.js'), js);
    writeFileSync(join(directory, 'feed.xml'), '<feed>\n  <title>Feed</title>\n</feed>');
    await minifySite(directory);
    const outputCSS = readFileSync(join(directory, 'assets/main.css'), 'utf8');
    const outputJS = readFileSync(join(directory, 'assets/posts.js'), 'utf8');
    assert.ok(outputCSS.length < css.length && outputCSS.includes('../image.png'));
    assert.ok(outputJS.length < js.length);
    const context = { window: {} };
    runInNewContext(outputJS, context);
    assert.equal(context.window.result, 42);
    assert.equal(readFileSync(join(directory, 'pagefind/pagefind.js'), 'utf8'), js);
    assert.equal(readFileSync(join(directory, 'feed.xml'), 'utf8'), '<feed>\n  <title>Feed</title>\n</feed>');
    await assert.rejects(minifySource('broken.js', 'function {'));
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
