"""Check the production output after npm run build; uses only Python's standard library."""
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.elements = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


site = Path('_site')
home = Page(site / 'index.html')
assert sum(tag == 'title' for tag, _ in home.elements) == 1
entries = json.loads(Path('_data/feed.json').read_text())['feed']['entry']
assert sum(a.get('class') == 'feed-card' for _, a in home.elements) == len(entries)
assert sum(a.get('class') == 'card__item h-entry' for _, a in home.elements) == 3
recent_images = [a for tag, a in home.elements if tag == 'img' and a.get('class') == 'post__img u-featured']
assert len(recent_images) == 3
assert all(a.get('fetchpriority') == 'high' and a.get('loading') != 'lazy' for a in recent_images)
assert (site / 'assets/images/bg.webp').stat().st_size < 50_000
for path in ['posts/index.html', 'about/index.html', 'submission/index.html', 'tag/index.html',
             'feed.xml', 'feed.xsl', 'feed.rss', 'feed.json', 'twtxt.txt', 'humans.txt', 'posts/feed.atom', 'sitemap.xml', '404.html', 'assets/main.css',
             'assets/js/posts.js', 'pagefind/pagefind-ui.js', 'pagefind/pagefind-ui.css']:
    assert (site / path).is_file(), path
for path in ['docs', 'scripts', 'tests', 'vendor', 'node_modules', 'assets/main.scss']:
    assert not (site / path).exists(), path
assert not list((site / 'posts').glob('page*/index.html'))
for tag, attrs in home.elements:
    if tag in ('script', 'link'):
        url = attrs.get('src', attrs.get('href', ''))
        assert 'bootstrap' not in url and 'sarissa' not in url, url
tag_ids = {attrs['id'] for _, attrs in Page(site / 'tag/index.html').elements if 'id' in attrs}
for page in site.rglob('*.html'):
    html = Page(page)
    if any(tag == 'header' for tag, _ in html.elements):
        assert sum(tag == 'main' for tag, _ in html.elements) == 1, page
        main = next(a for tag, a in html.elements if tag == 'main')
        assert main.get('id') == 'main-content' and main.get('tabindex') == '-1', page
        first_link = next(a for tag, a in html.elements if tag == 'a' and 'href' in a)
        assert first_link.get('class') == 'skip-link' and first_link['href'] == '#main-content', page
        assert sum(a.get('id') == 'main-content' for _, a in html.elements) == 1, page
        assert not any(int(a.get('tabindex', '0')) > 0 for _, a in html.elements), page
    for _, attrs in html.elements:
        if attrs.get('class') == 'p-category':
            assert attrs['href'].startswith('/tag/#'), (page, attrs)
            assert attrs['href'].split('#', 1)[1] in tag_ids, (page, attrs)
forms = [attrs for tag, attrs in Page(site / 'submission/index.html').elements if tag == 'form']
assert len(forms) == 1 and forms[0].get('method') == 'POST'

archive = Page(site / 'posts/index.html')
assert all(a.get('loading') == 'lazy' for tag, a in archive.elements if tag == 'img')
assert not any('style' in a and 'display' in a['style'] for tag, a in archive.elements if tag == 'article')
for page in [site / 'index.html', site / 'posts/index.html', site / '404.html']:
    html = Page(page)
    assert all('defer' in a for tag, a in html.elements if tag == 'script' and 'src' in a)
    assert sum(tag == 'style' for tag, _ in html.elements) == 1
    assert not any(tag == 'link' and a.get('href') == '/assets/main.css' for tag, a in html.elements)
    assert any(tag == 'link' and a.get('rel') == 'preload' and a.get('as') == 'style'
               and a.get('href') == '/pagefind/pagefind-ui.css' and 'onload' in a
               for tag, a in html.elements)
    assert '<style>' + Path('_includes/main.css').read_text() + '</style>' in page.read_text()
assert (site / 'assets/main.css').read_text().strip() == Path('_includes/main.css').read_text().strip()
assert json.loads((site / '.well-known/appspecific/com.chrome.devtools.json').read_text()) == {}

# Parse the formats as feed readers do, including escaping, dates, and identifiers.
rss = ET.parse(site / 'feed.rss').getroot()
assert rss.tag == 'rss' and rss.attrib['version'] == '2.0'
channel = rss.find('channel')
assert all(channel.findtext(key) for key in ['title', 'link', 'description'])
rss_items = channel.findall('item')
json_feed = json.loads((site / 'feed.json').read_text())
assert json_feed['version'] == 'https://jsonfeed.org/version/1.1'
assert json_feed['feed_url'] == 'https://relcfp.com/feed.json'
items = json_feed['items']
post_urls = {a['href'] for _, a in archive.elements if a.get('class') == 'u-url' and a.get('href', '').startswith('/')}
assert {item['url'].removeprefix('https://relcfp.com') for item in items} == post_urls
assert len(rss_items) == len(items) == len({item['id'] for item in items}) == len(post_urls)
for rss_item, item in zip(rss_items, items):
    assert rss_item.findtext('title') == item['title']
    assert rss_item.findtext('guid') == item['id'] == item['url']
    assert item['url'].startswith('https://relcfp.com/')
    assert isinstance(item['content_text'], str)
    assert datetime.fromisoformat(item['date_published']).tzinfo
    assert parsedate_to_datetime(rss_item.findtext('pubDate')).tzinfo
lines = [line for line in (site / 'twtxt.txt').read_text().splitlines() if line and not line.startswith('#')]
assert len(lines) == len(items)
for line, item in zip(lines, reversed(items)):
    timestamp, text = line.split('\t', 1)
    assert '\t' not in text
    assert datetime.fromisoformat(timestamp).isoformat() == datetime.fromisoformat(item['date_published']).isoformat()
    assert text.endswith(' ' + item['url'])
assert ET.parse(site / 'feed.xml').getroot().tag == '{http://www.w3.org/2005/Atom}feed'
assert ET.parse(site / 'feed.xsl').getroot().tag == '{http://www.w3.org/1999/XSL/Transform}stylesheet'
contributors = json.loads(Path('_data/contributors.json').read_text())
humans = (site / 'humans.txt').read_text()
for person in contributors['humans']:
    assert 'https://github.com/' + person['login'] in humans
assert not any(bot in humans for bot in contributors['automation'])
readme_users = re.findall(r'github\.com/([\w-]+)(?=[/)\s])', Path('README.md').read_text())
logins = {person['login'].lower() for person in contributors['humans']}
assert set(user.lower() for user in readme_users) <= logins | {'support-ukraine'}
assert 'https://creativitas.dev/' in humans
print(f'Built site verified: {len(items)} posts in RSS/JSON/twtxt, human credits, imported Atom, routes, search, and responsive assets.')
