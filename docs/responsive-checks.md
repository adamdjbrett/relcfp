RELCFP responsive cleanup — October 28, 2026

The site keeps its existing colors, typography style, and background. The custom
stylesheet is approximately 62% smaller: 18,542 bytes before this pass versus
approximately 7.1 KB afterward. No dependencies were added.

Removed unused About-component and legacy-search styles, redundant selectors,
repeated media queries, obsolete browser resets, and the redundant search startup
listener. Pagefind's generated CSS and JavaScript remain because live search uses
them. Its script now loads with `defer`; the archive script only loads on `/posts/`.

Responsive changes:

- Containers have fluid gutters and a 1200-pixel maximum width. Article text is
  limited to 72 characters per line; long URLs and titles can wrap.
- Cards use one, two, or three columns, with zero minimum grid widths to prevent
  long content expanding the page. Images preserve their proportions.
- Navigation wraps into balanced rows on very narrow phones. Navigation, submit,
  load-more, and footer social controls have at least 44-pixel heights.
- Form controls have readable 16-pixel text and fit their containers. Tables,
  author panels, tags, and previous/next links remain within the page width.
- The 404 styles are scoped to the error content, and author links use visible
  text instead of unavailable icon fonts.
- Archive thumbnails load lazily, and thumbnail dimensions reserve their layout
  space. Search has reserved space before its deferred script initializes.
- Archive cards remain visible without JavaScript. With JavaScript, the initial
  six cards and Load More behavior are preserved.
- There is no `overflow-x: hidden` or clipping workaround on the page.

Browser checks used Chrome with actual CSS viewport widths, accounting for the
browser's existing zoom setting:

| CSS viewport width | Page types checked | Horizontal overflow |
| ---: | ---: | --- |
| 320 | 9 | None |
| 390 | 9 | None |
| 768 | 9 | None |
| 1023 | 9 | None |
| 1366 | 9 | None |
| 1920 | 9 | None |
| 2560 | 9 | None |

The nine page types were home, archive, tags, About, submission, 404, the longest
article title, an article containing multiple tables, and an article with an
author panel. Checks compared document scroll width with client width and inspected
elements extending beyond either edge. Search initialized on all 63 page/size checks.

Additional verification:

- Every one of the 215 article URLs passed the document overflow check at 320 pixels.
- Populated search results passed at 320, 768, 1366, and 2560 pixels; “religion”
  returned 216 results.
- On a 320-pixel viewport, 70 Load More clicks revealed all 215 posts, hid the
  finished button, and caused no horizontal overflow.
- Mobile and laptop screenshots were visually inspected for spacing, legibility,
  image proportions, navigation, and card layout.
- The production build, built-site assertions, eight archive-script tests, and
  eight Python feed tests passed.

Not checked: physical devices, Safari/Firefox, or a live deployment. Chrome browser
extension errors were excluded from site diagnostics. Netlify form submission was
not exercised.
