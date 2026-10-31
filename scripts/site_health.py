#!/usr/bin/env python3
"""Read-only health checks for public showroom. No credentials, payments, or user data."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

BASE = "https://justicelinderman-creator.github.io/soppy-nbm-showroom/"
ROUTES = ("", "store/", "studio/", "free/", "privacy.html")

class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.css = []
        self.scripts = []
        self.inputs = 0
        self.noindex = False
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "link" and "stylesheet" in (attributes.get("rel") or ""):
            self.css.append(attributes.get("href", ""))
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])
        if tag == "input" and attributes.get("type") == "checkbox":
            self.inputs += 1
        if tag == "meta" and attributes.get("name", "").lower() == "robots":
            self.noindex = "noindex" in attributes.get("content", "").lower()

def load(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "NBM-Public-Site-Health/1.0"})
            with urlopen(request, timeout=15) as response:
                code = response.status
                body = response.read()
                if code != 200:
                    raise RuntimeError(f"HTTP {code} from {url}")
                return body.decode("utf-8")
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if i < attempts - 1:
                time.sleep(3 * (i + 1))
    raise AssertionError(f"Unable to load {url}: {last}")

checked = set()
for route in ROUTES:
    page_url = urljoin(BASE, route)
    html = load(page_url)
    document = PublicHTML()
    document.feed(html)
    assert document.noindex, f"Prelaunch privacy gate missing: {page_url}"
    assert len(document.css) == 1, f"Expected one stylesheet: {page_url}"
    if route == "free/":
        assert document.inputs == 12, f"Checklist changed unexpectedly: {page_url}"
        assert document.scripts == ["audit.js"], f"Audit application script missing: {page_url}"
        assert 'id="audit-score"' in html and 'id="copy-audit"' in html, f"Audit controls missing: {page_url}"
    if route == "store/":
        assert "Checkout not active" in html, "A purchase appears enabled before review"
    for href in document.links + document.css + document.scripts:
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        target, _ = urldefrag(urljoin(page_url, href))
        if not target.startswith(BASE):
            if target.startswith("https://justicelinderman-creator.github.io/"):
                raise AssertionError(f"Link left the showroom path: {href} on {page_url}")
            continue
        if target not in checked:
            load(target)
            checked.add(target)
    print("PASS", route or "/", "nav", len(document.links), "css", len(document.css), "scripts", len(document.scripts))
print(f"OK: {len(ROUTES)} live pages and {len(checked)} internal links/assets verified.")
