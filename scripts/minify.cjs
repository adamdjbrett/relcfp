const { readFileSync, readdirSync, writeFileSync } = require('node:fs');
const { extname, join, sep } = require('node:path');
const { minify: htmlMinify } = require('html-minifier-terser');
const CleanCSS = require('clean-css');
const { minify: jsMinify } = require('terser');

async function minifySource(file, source) {
  switch (extname(file)) {
    case '.html':
      return htmlMinify(source, {
        collapseWhitespace: true,
        conservativeCollapse: true,
        removeComments: true,
        minifyCSS: { rebase: false },
        minifyJS: true,
      });
    case '.css': {
      const result = new CleanCSS({ rebase: false }).minify(source);
      if (result.errors.length) throw new Error(result.errors.join('\n'));
      return result.styles;
    }
    case '.js':
    case '.mjs':
      return (await jsMinify(source, { module: extname(file) === '.mjs' })).code;
    default:
      return source;
  }
}

async function minifySite(directory) {
  let before = 0;
  let after = 0;
  let count = 0;
  for (const name of readdirSync(directory, { recursive: true })) {
    // Pagefind already optimizes its generated assets and uses hashed filenames.
    if (name.startsWith(`pagefind${sep}`) || !/\.(html|css|m?js)$/.test(name)) continue;
    const file = join(directory, name);
    const source = readFileSync(file, 'utf8');
    let result;
    try {
      result = await minifySource(file, source);
    } catch (error) {
      throw new Error(`Minifying ${file}: ${error.message}`, { cause: error });
    }
    writeFileSync(file, result);
    before += Buffer.byteLength(source);
    after += Buffer.byteLength(result);
    count++;
  }
  console.log(`Minified ${count} HTML/CSS/JS files: ${before} → ${after} bytes (${((1 - after / before) * 100).toFixed(1)}% smaller).`);
}

module.exports = { minifySource, minifySite };
if (require.main === module) minifySite('_site').catch(error => {
  console.error(error);
  process.exitCode = 1;
});
