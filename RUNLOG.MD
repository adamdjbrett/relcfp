# RUNLOG

## Summary
- Started: `2026-05-10T07:43:51+00:00`
- Completed: `2026-05-10T07:44:11+00:00`
- Status: `failed`
- Content changed: `false`
- Feed URL: `https://input.relcfp.com/feed.xml`
- GitHub event: `schedule`
- GitHub actor: `adamdjbrett`
- GitHub ref: `main`

## Events
- `2026-05-10T07:43:51+00:00` Backed up existing feed.xml to old_feed.xml.
- `2026-05-10T07:43:51+00:00` Fetching primary feed with requests from https://input.relcfp.com/feed.xml.
- `2026-05-10T07:43:51+00:00` primary requests status: 403
- `2026-05-10T07:43:51+00:00` primary requests returned status 403
- `2026-05-10T07:43:51+00:00` Falling back to curl for primary feed.
- `2026-05-10T07:43:51+00:00` primary curl status: 403
- `2026-05-10T07:43:51+00:00` primary curl returned status 403
- `2026-05-10T07:43:51+00:00` Fetching fallback 1 feed with requests from https://input-relcfp.netlify.app/feed.xml.
- `2026-05-10T07:44:04+00:00` fallback 1 requests failed: HTTPSConnectionPool(host='input-relcfp.netlify.app', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input-relcfp.netlify.app', port=443): Failed to resolve 'input-relcfp.netlify.app' ([Errno -2] Name or service not known)"))
- `2026-05-10T07:44:04+00:00` Falling back to curl for fallback 1 feed.
- `2026-05-10T07:44:11+00:00` fallback 1 curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input-relcfp.netlify.app/feed.xml']' returned non-zero exit status 6.
- `2026-05-10T07:44:11+00:00` Feed update failed: primary requests returned status 403; primary curl returned status 403; fallback 1 requests failed: HTTPSConnectionPool(host='input-relcfp.netlify.app', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input-relcfp.netlify.app', port=443): Failed to resolve 'input-relcfp.netlify.app' ([Errno -2] Name or service not known)")); fallback 1 curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input-relcfp.netlify.app/feed.xml']' returned non-zero exit status 6.

## Errors
- `2026-05-10T07:43:51+00:00` primary requests returned status 403
- `2026-05-10T07:43:51+00:00` primary curl returned status 403
- `2026-05-10T07:44:04+00:00` fallback 1 requests failed: HTTPSConnectionPool(host='input-relcfp.netlify.app', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input-relcfp.netlify.app', port=443): Failed to resolve 'input-relcfp.netlify.app' ([Errno -2] Name or service not known)"))
- `2026-05-10T07:44:11+00:00` fallback 1 curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input-relcfp.netlify.app/feed.xml']' returned non-zero exit status 6.
- `2026-05-10T07:44:11+00:00` Feed update failed: primary requests returned status 403; primary curl returned status 403; fallback 1 requests failed: HTTPSConnectionPool(host='input-relcfp.netlify.app', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input-relcfp.netlify.app', port=443): Failed to resolve 'input-relcfp.netlify.app' ([Errno -2] Name or service not known)")); fallback 1 curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input-relcfp.netlify.app/feed.xml']' returned non-zero exit status 6.
