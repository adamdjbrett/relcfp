[![Support Ukraine Badge](https://bit.ly/support-ukraine-now)](https://github.com/support-ukraine/support-ukraine) [![Jekyll](https://img.shields.io/badge/built%20for-Jekyll-red.svg)](https://jekyllrb.com/) [![Daily rebuild](https://github.com/adamdjbrett/relcfp/actions/workflows/cronjob.yml/badge.svg)](https://github.com/adamdjbrett/relcfp/actions/workflows/cronjob.yml)
[![Netlify Status](https://api.netlify.com/api/v1/badges/5c53356c-5f0f-45a4-9d4c-6beb309f66ee/deploy-status)](https://app.netlify.com/sites/relcfp/deploys)
# Religion Call for Papers | RELCFP
The new and improved 2.0 version of relcfp.

## Contributors
* Thank you to [@leno4ka94](https://github.com/leno4ka94) for the Jekyll theme.

<a href="https://github.com/adamdjbrett/relcfp/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=adamdjbrett/relcfp" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## Image Credit
[notebook phone](https://pixabay.com/images/id-2846221/)

## Development

Use Ruby 3.3.6 (see `.ruby-version`) and Node.js with npm. The site deploys on Netlify.

```sh
bundle config set --local path vendor/bundle
bundle install
npm ci
npm run build
npm run dev
```

`npm run build` generates `_site/` and then the Pagefind search index. After a new
checkout, build once before starting the development server so search assets exist.
Edit `assets/main.css` directly; there is no Sass compilation step for site styles.
Jekyll 3 still installs its own Sass converter as a transitive dependency.

## Repository layout

- `_posts/`, `pages/`, `_data/`: content and navigation data. `pages/index.html` is the homepage; `pages/feed/` holds the feed templates.
- `_layouts/`, `_includes/`: shared Liquid templates.
- `assets/`: plain CSS, browser JavaScript, images, and downloadable PDFs.
- `scripts/get_rss.py`: feed maintenance, run from the repository root.
- `tests/`: feed regressions, browser-script checks, and built-site checks.
- `docs/`: audit results, maintenance run log, historical technology reports, and archived theme files.
- `_site/`, `vendor/`, `node_modules/`, `.venv/`: ignored local build/dependency output.

## Checks and feed maintenance

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
npm test
npm run build
python3 tests/check_site.py
```

To refresh the feed, run `.venv/bin/python scripts/get_rss.py` from this directory.
This writes `pages/feed/feed.xml`, `_data/feed.json`, and `docs/RUNLOG.md`. The homepage renders the
saved JSON during the build. The scheduled GitHub workflow refreshes it separately.

See [the optimization audit](docs/audit.md) for findings and measurements.

The responsive stylesheet keeps the existing colors and background, uses fluid text
and bounded reading widths, and changes card grids by screen size. Archive images
load lazily; all archive posts remain visible if JavaScript is disabled. Search
scripts are deferred, and `keep_files` preserves the generated search bundle during
Jekyll's local rebuilds. Run a production build again to refresh search content.

See [responsive checks](docs/responsive-checks.md) for screen sizes and browser results.

## Feeds and credits

The production build publishes every curated post in three formats:

- [RSS 2.0](https://relcfp.com/feed.rss)
- [JSON Feed 1.1](https://relcfp.com/feed.json)
- [twtxt](https://relcfp.com/twtxt.txt), with the oldest posts first

The imported feed remains at `/feed.xml`, its stylesheet at `/feed.xsl`, and the
existing curated Atom feed at `/posts/feed.atom`. Feed templates have no HTML layout
and are excluded from the sitemap. Netlify sets the feed content types.

[humans.txt](https://relcfp.com/humans.txt) credits all human GitHub contributors
checked on October 28, 2026, the theme author thanked in this README, and the
existing Creativitas acknowledgment. `_data/contributors.json` records the source
and excludes the two automation accounts from the human list. Refresh that list
from GitHub when contributors change; builds do not need a GitHub connection.

Root files are limited to conventional project/build entry points and the favicon.
The Python requirements are in `scripts/requirements.txt`; maintenance logs and
historical theme material are under `docs/`. Pagefind's default glob and indexed
content boundaries replace the redundant root configuration file.
