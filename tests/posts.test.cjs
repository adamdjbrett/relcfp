const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');

const source = readFileSync('assets/js/posts.js', 'utf8');
for (const count of [0, 3, 6, 7, 8, 9, 10, 215]) {
  test(`Load More finishes safely with ${count} posts`, () => {
    const button = {};
    const boxes = Array.from({ length: count }, () => ({ hidden: false }));
    runInNewContext(source, {
      document: { querySelector: () => button, querySelectorAll: () => boxes },
    });
    assert.equal(button.hidden, count <= 6);
    assert.equal(boxes.filter(box => !box.hidden).length, Math.min(6, count));
    let clicks = 0;
    while (!button.hidden && clicks++ < count) button.onclick();
    assert.equal(button.hidden, true);
    assert.ok(boxes.every(box => !box.hidden));
  });
}
