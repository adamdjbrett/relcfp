# RUNLOG

## Summary
- Started: `2026-04-07T02:29:45+00:00`
- Completed: `2026-04-07T02:30:04+00:00`
- Status: `failed`
- Content changed: `false`
- Feed URL: `https://input.relcfp.com/feed.xml`
- GitHub event: `local`
- GitHub actor: `local`
- GitHub ref: `local`

## Events
- `2026-04-07T02:29:45+00:00` Backed up existing feed.xml to old_feed.xml.
- `2026-04-07T02:29:45+00:00` Fetching feed with requests from https://input.relcfp.com/feed.xml.
- `2026-04-07T02:29:57+00:00` requests failed: HTTPSConnectionPool(host='input.relcfp.com', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input.relcfp.com', port=443): Failed to resolve 'input.relcfp.com' ([Errno 8] nodename nor servname provided, or not known)"))
- `2026-04-07T02:29:57+00:00` Falling back to curl.
- `2026-04-07T02:30:04+00:00` curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input.relcfp.com/feed.xml']' returned non-zero exit status 6.
- `2026-04-07T02:30:04+00:00` Feed update failed: requests failed: HTTPSConnectionPool(host='input.relcfp.com', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input.relcfp.com', port=443): Failed to resolve 'input.relcfp.com' ([Errno 8] nodename nor servname provided, or not known)")); curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input.relcfp.com/feed.xml']' returned non-zero exit status 6.

## Errors
- `2026-04-07T02:29:57+00:00` requests failed: HTTPSConnectionPool(host='input.relcfp.com', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input.relcfp.com', port=443): Failed to resolve 'input.relcfp.com' ([Errno 8] nodename nor servname provided, or not known)"))
- `2026-04-07T02:30:04+00:00` curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input.relcfp.com/feed.xml']' returned non-zero exit status 6.
- `2026-04-07T02:30:04+00:00` Feed update failed: requests failed: HTTPSConnectionPool(host='input.relcfp.com', port=443): Max retries exceeded with url: /feed.xml (Caused by NameResolutionError("HTTPSConnection(host='input.relcfp.com', port=443): Failed to resolve 'input.relcfp.com' ([Errno 8] nodename nor servname provided, or not known)")); curl failed: Command '['curl', '--silent', '--show-error', '--location', '--compressed', '--retry', '3', '--retry-all-errors', '--connect-timeout', '15', '--max-time', '60', '-A', 'Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)', '-H', 'Accept: application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8', '-H', 'Accept-Language: en-US,en;q=0.9', '-H', 'Cache-Control: no-cache', '-H', 'Pragma: no-cache', '--write-out', '\n__CURL_HTTP_STATUS__:%{http_code}', 'https://input.relcfp.com/feed.xml']' returned non-zero exit status 6.
