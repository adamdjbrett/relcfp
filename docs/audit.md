What this repo does: RELCFP publishes a Jekyll archive of religion calls for papers,
plus a homepage feed maintained by a scheduled Python job. Netlify builds the site;
Pagefind supplies browser search. This audit assumes one maintainer and static-site
traffic, with no application server or database.

Audit and optimization completed locally on October 28, 2026. Changes are not deployed.

## Measurements

Three alternating baseline/updated runs used Ruby 3.3.6, the same installed gems,
and the same Pagefind executable. Full-build times include Jekyll startup and
Pagefind; they exclude dependency installation and network fetches. Medians:

| Measure | Before | After | Change |
| --- | ---: | ---: | ---: |
| Full build | 2.467 s | 1.697 s | 31% faster |
| Jekyll rendering | 1.519 s | 1.186 s | 22% faster |
| Unique resolved Ruby gems | 95 | 32 | 63 removed |
| Generated HTML pages | 258 | 223 | 35 duplicate pages removed |
| Generated HTML | 6.29 MB | approximately 5.35 MB | approximately 15% smaller |
| Complete built site, including search and media | 32.76 MB | approximately 31.76 MB | approximately 3% smaller |
| Local vendor directory | 112 MiB | 24 MiB | unused gems pruned |

These are local measurements, not a promise about Netlify build times. Media still
accounts for approximately 24 MiB of the output. No new dependencies were added to
npm; Pagefind remains the only direct npm dependency.

## Must fix — completed

1. **The last archive batch could crash** (`assets/js/posts.js`).
   - **What this is:** The archive initially shows six posts, then reveals three per click.
   - **Problem:** The old loop accessed nonexistent cards when the final batch contained fewer than three posts.
   - **Fix:** Reveal a bounded slice, hide the finished button, and use a keyboard-accessible button. Eight Node tests cover empty, short, partial, and full archives.
   - **If skipped:** Visitors cannot reliably reveal the last posts.

2. **The submission form used GET** (`pages/submission.html`).
   - **What this is:** Visitors submit messages and optional attachments through Netlify Forms.
   - **Problem:** Without a method, browsers default to GET; submitted fields can appear in the URL, and attachment submission does not work correctly. The markup also contained nested labels and an extra closing form tag.
   - **Fix:** Set POST, retain multipart encoding, repair the markup, and give the text fields accessible names.
   - **If skipped:** The form does not submit as intended. A built-site check now verifies its method and form count.

3. **Feed failures looked successful to automation** (`scripts/get_rss.py`).
   - **What this is:** The scheduled job downloads and saves the upstream feed.
   - **Problem:** Its exception handler logged failure but exited successfully.
   - **Fix:** Restore the previous XML feed, clear pending social-post data, and propagate the exception. A regression test verifies restoration and failure outputs.
   - **If skipped:** A failed refresh can pass unnoticed. The workflow also now excludes pull requests from the deploy-hook step.

4. **Post tag links pointed at a missing page** (`_layouts/post.html`, `pages/posts.html`).
   - **What this is:** Tags link from individual posts and archive cards to the tag directory.
   - **Problem:** Links used `/tag.html`, while the page is published at `/tag/`.
   - **Fix:** Use `/tag/` and consistent escaped anchors. Netlify redirects the legacy page URL. Built-site checks verify every post tag anchor.
   - **If skipped:** Clicking tags leads to a missing page.

## Should fix — completed

5. **Most installed Ruby gems were unused** (`Gemfile`, `Gemfile.lock`, `_config.yml`).
   - **What this is:** The GitHub Pages bundle installs numerous themes and plugins.
   - **Problem:** This site deploys through Netlify and uses its own layouts. The bundle pulled in 63 unnecessary resolved gems.
   - **Fix:** Declare Jekyll and the plugins actually used: feed, SEO, sitemap, and redirects. Keep the GFM Markdown parser and local-server dependencies. Regenerate the lockfile and prune the project's local bundle.
   - **If skipped:** Installs carry unnecessary downloads, disk usage, and maintenance work.

6. **The browser rebuilt a feed already available at build time** (`_includes/fetcher.html`).
   - **What this is:** The homepage lists the saved upstream feed.
   - **Problem:** It downloaded XML again, assembled HTML in JavaScript, repeated an element ID, and loaded Bootstrap twice. Every page also loaded an unused legacy XML compatibility library.
   - **Fix:** Render the saved JSON with Liquid, escape feed text, and use a small CSS grid. Remove Bootstrap, Sarissa, abandoned feed templates, and commented-out browser rendering code.
   - **If skipped:** Feed display depends on JavaScript and another request after loading the page.

7. **Pagination generated duplicate homepages** (`_config.yml`, `netlify.toml`).
   - **What this is:** The pagination plugin copied the root homepage to `/posts/page2/` through `/posts/page36/`.
   - **Problem:** Those pages did not display paginated archive content; the archive uses Load More.
   - **Fix:** Remove the unused pagination plugin/configuration and redirect its old URLs to `/posts/` on Netlify.
   - **If skipped:** Each build produces and publishes 35 redundant pages.

8. **Build and repository work could be simpler** (`assets/main.css`, `pages/tag.html`, `scripts/`, `docs/`).
   - **What this is:** Sass compiled styles that can be maintained as CSS; the tags template repeatedly looked up the same tag map.
   - **Problem:** Styles required an unnecessary source compilation step, tag rendering repeated work, bytecode was tracked, and maintenance files cluttered the root.
   - **Fix:** Preserve the compiled style rules as editable CSS, remove all Sass sources, sort the tag map once, move the feed script and historical reports into dedicated folders, remove tracked bytecode, and update callers and documentation. Remove duplicate document titles, duplicate page images, and obsolete Pagefind configuration keys; restore visible keyboard focus.
   - **If skipped:** Maintainers keep working around unnecessary build and source-tree complexity.

## Validation and limits

- Production build succeeds after pruning unused gems.
- Eight Python feed tests and eight Node archive tests pass.
- Built-site checks cover feed/recent-post counts, public routes, search assets, tag anchors, form method, one document title, and private build-file exclusions.
- All 215 existing post bodies match the baseline HTML exactly. Existing post redirects remain generated.
- Pagefind still indexes 216 pages. Browser search for “religion” returns results.
- Desktop and narrow mobile previews have no horizontal overflow; the feed switches to one column. The live archive reveals six then nine posts.
- CSS comes from the original compiler output. There is no site Sass source or stylesheet compilation step; Jekyll 3 itself still requires its Sass converter transitively.
- Images and PDFs retain their existing files and URLs. They were not recompressed or removed merely because a local reference was absent.
- Netlify redirects and form delivery need deployed verification. No form was submitted, social message sent, or live feed refresh performed.
- Historical technology reports under `docs/` are explicitly marked historical; they are not current dependency inventories.

Configuration was checked against the [Jekyll configuration documentation](https://jekyllrb.com/docs/configuration/options/)
and [Pagefind CLI configuration documentation](https://pagefind.app/docs/config-options/).

Verdict: The requested cleanup is implemented and locally verified; deployment verification remains.
Lean: -1,779 source/documentation lines, -63 resolved Ruby dependencies (implemented).
Not checked: Production deploy, Netlify form delivery and redirects, external feed availability, or a full dependency vulnerability scan.

The subsequent [CSS and responsive pass](responsive-checks.md) records the current
stylesheet size and mobile/laptop/wide-screen verification.

## Lighthouse fixes — October 29, 2026

The supplied desktop report for https://relcfp.com/ (Lighthouse run at
2026-10-29T14:28:54Z) scored performance 99, accessibility 98, best practices 100,
and SEO 100. It reported LCP 0.9 seconds.

- Added one main landmark around page content in the shared layout, covering
  the homepage, archive, posts, and information pages.
- Added `fetchpriority="high"` to the three homepage recent-post images. The
  middle image was the reported desktop LCP; all three can be visible together.
  Archive thumbnails remain lazy-loaded.
- Recompressed `assets/images/bg.webp` with `cwebp -q 75`, preserving its URL and
  1060 × 722 dimensions: 156,916 to 37,532 bytes (76% smaller).
- Extended the built-site checks for main landmarks, eager priority images,
  and the background size budget.

Jekyll built with the project's Ruby 3.3.6; Pagefind indexed 216 pages. All eight
Node tests and the built-site checks passed. A local desktop Lighthouse audit
scored accessibility, best practices, and SEO 100 with no failing audits. This
audit tool does not score performance. A local cold-load trace confirmed CLS 0
and no LCP discovery warning; local timings are not comparable to production.
The rendered desktop page and 390px mobile layout were checked for overflow.

The reported unminified/unused JavaScript belongs entirely to browser extensions.
The cache warnings refer to Cloudflare's injected analytics and email-protection
scripts, whose headers are outside this repository. Stylesheet changes were
skipped because Lighthouse estimated zero FCP/LCP savings. No new dependency or
Cloudflare setting was introduced. Changes are local and need a deployed audit.

Implementation guidance: [Chrome LCP request discovery](https://developer.chrome.com/docs/performance/insights/lcp-discovery)
and [image delivery](https://developer.chrome.com/docs/performance/insights/image-delivery).

Follow-up: the shared head preconnects to `static.cloudflareinsights.com`.
The email-decoder prefetch was subsequently removed at the user's request:
the homepage needs no speculative email-decoder download. Cloudflare manages
decoder injection for protected email addresses; the templates add no decoder
script or prefetch in either the head or footer. The decoder uses the existing
same-origin connection, so it needs no preconnect. Resource hints do not change
Cloudflare cache lifetimes.

## Keyboard accessibility — October 29, 2026

- The first tab stop is now a high-contrast “Skip to content” link. It appears
  on focus and moves focus to `main#main-content` on Enter, without JavaScript.
  The next Tab reaches the first content link. The target uses `tabindex="-1"`
  so it does not add an extra stop to ordinary tab navigation.
- Main navigation has an accessible name and marks the active link with
  `aria-current="page"`. Native links and buttons retain normal tab order and
  visible focus indicators; no positive tabindex values were added.
- Load More focuses the first newly revealed post link, including the final
  partial batch, so users can continue through new content instead of skipping
  to the footer. The eight archive tests now check this focus handoff.
- Submission fields have persistent visible labels; name and email expose
  standard autocomplete purposes.

Browser checks verified the skip link's first Tab, visibility, Enter activation,
and next Tab; archive Enter activation (six to nine posts, focus on post seven);
forward/reverse tabbing through form fields; and tabbing to search results and
keyboard activation of Clear. Built-site checks verify skip links, unique main
targets, and no positive tabindex on every page using the shared layout.
The build, Pagefind index, eight Node tests, and built-site checks pass.

Local Lighthouse accessibility is 100 for the desktop homepage and mobile
submission page. Both audits logged the expected local 404 for the previously
requested Cloudflare decoder prefetch: `/cdn-cgi/` is served by Cloudflare in
production, not the local preview. These results do not certify full WCAG 2.2 AA
conformance across all historical post content, assistive technologies, or
browsers. No screen-reader session or production deployment was performed.

The skip link follows [W3C technique G1](https://www.w3.org/WAI/WCAG22/Techniques/general/G1);
focus behavior follows [WCAG focus-order guidance](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html).

## Local render-blocking requests — October 29, 2026

At the user's request, the shared head now inlines the small site stylesheet
and asynchronously preloads Pagefind CSS, with a noscript stylesheet fallback.
`_includes/main.css` is the single editable source; `/assets/main.css` remains
available from that source for existing links. Inlining adds about 8 KB to each
HTML document in exchange for eliminating the separate blocking CSS request.

`pages/devtools.json` publishes `{}` at
`/.well-known/appspecific/com.chrome.devtools.json`, excluded from the sitemap.
This answers Chrome's workspace probe without exposing a local path or enabling
automatic workspace mapping.

Verified against the running Jekyll server at http://localhost:4000/: the probe
returns HTTP 200 and valid JSON; main CSS makes no network request; Pagefind CSS
applies successfully; search renders; and there is no horizontal overflow.
A cold-load trace reports CLS 0 and no RenderBlocking or NetworkDependencyTree
insights. Local desktop Lighthouse scores accessibility, best practices, and SEO
100, with zero failed audits. The build, Pagefind index, eight Node tests, and
built-site assertions pass. Production performance has not been remeasured.

References: [asynchronous CSS loading](https://web.dev/articles/defer-non-critical-css)
and [Chrome automatic workspaces](https://developer.chrome.com/docs/devtools/automatic-workspaces).
