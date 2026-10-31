#!/usr/bin/env python3
"""Public showroom smoke test. No credentials, payments, or customer data."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

BASE = "https://justicelinderman-creator.github.io/soppy-nbm-showroom/"
ROUTES = ("", "store/", "studio/", "free/", "demo/detailflow/", "privacy.html")

class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.css = []
        self.scripts = []
        self.checkboxes = 0
        self.forms = 0
        self.robots = ""
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "link" and "stylesheet" in (attributes.get("rel") or ""):
            self.css.append(attributes.get("href", ""))
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])
        if tag == "form":
            self.forms += 1
        if tag == "input" and attributes.get("type") == "checkbox":
            self.checkboxes += 1
        if tag == "meta" and attributes.get("name", "").lower() == "robots":
            self.robots = attributes.get("content", "").lower()

def load(url, attempts=3):
    last = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "NBM-Public-Site-Health/2.0"})
            with urlopen(request, timeout=18) as response:
                assert response.status == 200, f"HTTP {response.status}: {url}"
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, AssertionError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 * (attempt + 1))
    raise AssertionError(f"HTTP/read failure {url}: {last}")

# GitHub Pages can lag behind the source commit that starts Actions.
# Wait until all newly published release assets are actually live.
for attempt in range(16):
    try:
        free_latest = load(BASE + "free/?release=" + str(attempt), attempts=1)
        demo_latest = load(BASE + "demo/detailflow/?release=" + str(attempt), attempts=1)
        robots_latest = load(BASE + "robots.txt?release=" + str(attempt), attempts=1)
        sitemap_latest = load(BASE + "sitemap.xml?release=" + str(attempt), attempts=1)
        if ('content="index,follow"' in free_latest
            and "No messages or payments accepted" in demo_latest
            and "Sitemap:" in robots_latest
            and "<urlset" in sitemap_latest):
            break
    except AssertionError:
        pass
    if attempt == 15:
        raise AssertionError("GitHub Pages did not finish publishing the latest public release")
    time.sleep(5)

assert "Allow: /" in robots_latest, "robots.txt does not permit audit discovery"
assert BASE + "free/" in sitemap_latest, "Free audit missing from sitemap"
assert BASE + "store/" not in sitemap_latest, "Unready checkout listed as indexable"

checked = set()
for route in ROUTES:
    page_url = urljoin(BASE, route)
    html = load(page_url)
    document = PublicHTML()
    document.feed(html)
    is_audit = route == "free/"
    if is_audit:
        assert "index" in document.robots and "noindex" not in document.robots, "Free audit not indexable"
        assert document.checkboxes == 12, "The 12-point audit changed"
        assert document.scripts == ["audit.js"], "Free audit JavaScript missing"
        assert 'id="audit-score"' in html and 'id="copy-audit"' in html, "Audit interaction missing"
        assert '<link rel="canonical"' in html, "Free audit canonical link missing"
    else:
        assert "noindex" in document.robots, f"Unready page accidentally became indexable: {route}"
    if route == "store/":
        assert "Checkout not active" in html, "Store checkout gate missing"
        assert "../demo/detailflow/" in html, "Store demo link missing"
    if route == "studio/":
        assert "../demo/detailflow/" in html, "Studio demo link missing"
    if route == "demo/detailflow/":
        assert document.forms == 0, "Public product sample has a data-collecting form"
        assert "Submitting inquiries is disabled" in html, "Demo submit gate missing"
        assert not document.scripts, "Demo loads unexpected external script"
        assert not document.css, "Demo loads unexpected external stylesheet"
    else:
        assert len(document.css) == 1, f"Expected one stylesheet at {route}"
    for href in document.links + document.css + document.scripts:
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        target, _ = urldefrag(urljoin(page_url, href))
        if target.startswith("https://justicelinderman-creator.github.io/") and not target.startswith(BASE):
            raise AssertionError(f"Broken nested path: {href} on {route}")
        if target.startswith(BASE) and target not in checked:
            load(target)
            checked.add(target)
    print("PASS", route or "/", "links", len(document.links),
          "css", len(document.css), "scripts", len(document.scripts))
print("PASS: public navigation, prelaunch gates, safe demo and free-audit indexing.")
