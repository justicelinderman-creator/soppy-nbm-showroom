#!/usr/bin/env python3
"""Public showroom smoke test. No credentials, payments, or customer data."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from hashlib import sha256
from pathlib import Path
import time

BASE = "https://justicelinderman-creator.github.io/soppy-nbm-showroom/"
ROUTES = ("", "game-assets/", "services/", "services/n8n/", "roblox-qa/", "guides/roblox-release-checklist/", "guides/n8n-webhook-reliability/", "tools/workflow-preflight/", "store/", "studio/", "free/", "demo/detailflow/", "privacy.html", "portfolio/facility-console/", "creatorops/", "creatorops/checker/")
INDEXABLE = {"", "game-assets/", "services/", "services/n8n/", "roblox-qa/", "guides/roblox-release-checklist/", "guides/n8n-webhook-reliability/", "tools/workflow-preflight/", "free/", "studio/", "portfolio/facility-console/", "creatorops/", "creatorops/checker/"}

class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.css = []
        self.scripts = []
        self.checkboxes = 0
        self.forms = 0
        self.robots = ""
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "img" and attributes.get("src"):
            self.images.append(attributes["src"])
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

def load(url, attempts=3, timeout=18):
    last = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": "NBM-Public-Site-Health/2.0"})
            with urlopen(request, timeout=timeout) as response:
                assert response.status == 200, f"HTTP {response.status}: {url}"
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, AssertionError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 * (attempt + 1))
    raise AssertionError(f"HTTP/read failure {url}: {last}")

def wait_for_release():
    """Wait for this checkout's public assets, not just older discovery pages."""
    root = Path(__file__).resolve().parents[1]
    expected = {route: (root / source).read_text(encoding="utf-8") for route, source in (
        ("studio/", "studio/index.html"),
        ("roblox-qa/", "roblox-qa/index.html"),
        ("guides/roblox-release-checklist/", "guides/roblox-release-checklist/index.html"),
        ("guides/n8n-webhook-reliability/", "guides/n8n-webhook-reliability/index.html"),
        ("roblox-qa/example-report.txt", "roblox-qa/example-report.txt"),
        ("services/", "services/index.html"),
        ("services/n8n/", "services/n8n/index.html"),
        ("services/n8n/brief.js", "services/n8n/brief.js"),
        ("tools/workflow-preflight/", "tools/workflow-preflight/index.html"),
        ("assets/inquiry.css", "assets/inquiry.css"),
        ("assets/inquiry.js", "assets/inquiry.js"),
        ("creatorops/checker/radar.js", "creatorops/checker/radar.js"),
    )}
    release_key = sha256("\0".join(expected.values()).encode("utf-8")).hexdigest()[:16]
    # Pages builds run alongside this push-triggered check; the prior release
    # exceeded 90 seconds even though its eventual deployment succeeded.
    deadline = time.monotonic() + 240
    attempt = 0
    last = "Release assets are not current"

    def current(route):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise AssertionError("Release wait budget exhausted")
        url = BASE + route + "?release=" + release_key + "&attempt=" + str(attempt)
        value = load(url, attempts=1, timeout=min(18, remaining))
        if time.monotonic() >= deadline:
            raise AssertionError("Release wait budget exhausted")
        return value

    while time.monotonic() < deadline:
        try:
            free_latest = current("free/")
            demo_latest = current("demo/detailflow/")
            robots_latest = current("robots.txt")
            sitemap_latest = current("sitemap.xml")
            assert ('content="index,follow"' in free_latest
                and "No messages or payments accepted" in demo_latest
                and "Sitemap:" in robots_latest
                and "<urlset" in sitemap_latest
                and BASE + "studio/" in sitemap_latest
                and BASE + "roblox-qa/" in sitemap_latest
                and BASE + "guides/roblox-release-checklist/" in sitemap_latest
                and BASE + "guides/n8n-webhook-reliability/" in sitemap_latest
                and BASE + "portfolio/facility-console/" in sitemap_latest
                and BASE + "creatorops/" in sitemap_latest
                and BASE + "creatorops/checker/" in sitemap_latest), "Core release pages are not ready"
            for route, content in expected.items():
                assert current(route) == content, "Release asset not current: " + route
            return free_latest, demo_latest, robots_latest, sitemap_latest
        except (AssertionError, UnicodeError) as exc:
            last = str(exc)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(5, remaining))
        attempt += 1
    raise AssertionError("GitHub Pages did not finish publishing the latest public release within 240 seconds: " + last)


free_latest, demo_latest, robots_latest, sitemap_latest = wait_for_release()

assert "Allow: /" in robots_latest, "robots.txt does not permit audit discovery"
assert BASE + "free/" in sitemap_latest, "Free audit missing from sitemap"
assert BASE + "studio/" in sitemap_latest, "Indexable paid-service route missing from sitemap"
assert BASE + "portfolio/facility-console/" in sitemap_latest, "Original art portfolio missing from sitemap"
assert BASE + "creatorops/" in sitemap_latest, "Studio Companion educational preview missing from sitemap"
assert BASE + "creatorops/checker/" in sitemap_latest, "Useful XML checker missing from sitemap"
assert BASE + "store/" not in sitemap_latest, "Unready checkout listed as indexable"
assert BASE + "roblox-qa/" in sitemap_latest, "Scoped QA service inquiry route missing from sitemap"
assert BASE + "guides/roblox-release-checklist/" in sitemap_latest, "Roblox learning page missing from sitemap"
assert BASE + "guides/n8n-webhook-reliability/" in sitemap_latest, "Automation education page missing from sitemap"

checked = set()
for route in ROUTES:
    page_url = urljoin(BASE, route)
    html = load(page_url)
    document = PublicHTML()
    document.feed(html)
    is_audit = route == "free/"
    if route in INDEXABLE:
        directives = set(document.robots.replace(" ", "").split(","))
        assert {"index", "follow"} <= directives and "noindex" not in directives, f"Approved page not indexable: {route}"
        assert '<link rel="canonical"' in html, f"Canonical URL missing: {route}"
    else:
        assert "noindex" in document.robots, f"Unready page accidentally became indexable: {route}"
    if is_audit:
        assert document.checkboxes == 12, "The 12-point audit changed"
        assert document.scripts == ["audit.js"], "Free audit JavaScript missing"
        assert 'id="audit-score"' in html and 'id="copy-audit"' in html, "Audit interaction missing"
    if route == "store/":
        assert "Checkout not active" in html, "Store checkout gate missing"
        assert "../demo/detailflow/" in html, "Store demo link missing"
    if route in ("guides/roblox-release-checklist/", "guides/n8n-webhook-reliability/"):
        assert document.forms == 0 and not document.scripts, "Education page unexpectedly collects data or executes scripts"
        assert "No" in html or "no" in html, "Guide text missing"
        assert "https://buy.stripe.com" not in html and "checkout.shopify.com" not in html, "Guide must not activate checkout"
        if route == "guides/roblox-release-checklist/":
            assert "../../roblox-qa/" in html and "../../creatorops/checker/" in html, "Roblox guide lacks useful next steps"
            assert "not Roblox certification" in html.lower() or "not roblox certification" in html.lower(), "Roblox guide lacks independence disclosure"
        else:
            assert "../../services/n8n/" in html and "../../tools/workflow-preflight/" in html, "Automation guide lacks useful next steps"
            assert "not proof of a deployed customer crm" in html.lower(), "Automation guide implies client acceptance"
    if route == "roblox-qa/":
        assert document.forms == 0 and not document.scripts, "QA service page unexpectedly collects data or loads scripts"
        assert "NO CHECKOUT" in html and "1,500 Robux" not in html, "QA payment/readiness gate changed"
        assert "mailto:justice.linderman@gmail.com" in html and "example-report.txt" in html, "QA email/report route missing"
    if route == "studio/":
        assert "../demo/detailflow/" in html, "Studio demo link missing"
        assert "../portfolio/facility-console/" in html, "Studio original-portfolio link missing"
        assert "mailto:justice.linderman@gmail.com" in html, "Studio mailto route missing"
    if route == "creatorops/checker/":
        assert document.forms == 0, "No forms/remote intake allowed in free checker"
        assert document.scripts == ["./engine.js", "./radar.js"], "Local read-only checker scripts changed"
        assert "connect-src 'none'" in html, "Browser XML checker must block external requests"
        assert 'type="file"' in html, "Local file chooser missing"
        assert "No uploads" in html, "Local-only privacy disclosure missing"
        assert 'id="results"' in html and 'id="download"' in html, "Working report UI missing"
    if route == "creatorops/":
        assert "checker/" in html, "CreatorOps landing must link to the working free utility"

        assert document.forms == 0 and not document.scripts, "Beta-preview page unexpectedly has forms/scripts"
        assert "mailto:justice.linderman@gmail.com" in html, "Beta-interest email contact missing"
        assert "NOT AVAILABLE FOR DOWNLOAD" in html, "Unfinished plugin lacks release gate"
        assert "Native Studio trial pending" in html, "Native acceptance limitations missing"
        assert "no downloadable beta" in html.lower(), "Beta interest may be mistaken for an active plugin"
    if route == "portfolio/facility-console/":
        assert len(document.images) == 3, "Portfolio original image set changed"
        assert "mailto:justice.linderman@gmail.com" in html, "Original portfolio inquiry route absent"
        assert "not</strong> independently verified" in html, "Original Blender QA limitations not disclosed"
        assert '<meta property="og:image"' in html, "Portfolio social sharing art absent"
        assert document.forms == 0 and not document.scripts, "Portfolio unexpectedly collects data or loads scripts"
        for image in document.images:
            image_url=urljoin(page_url,image)
            with urlopen(Request(image_url,headers={"User-Agent":"NBM-Public-Site-Health/2.0"}),timeout=18) as image_response:
                assert image_response.status == 200, f"Original image missing: {image_url}"
                assert image_response.headers.get("Content-Type","").startswith("image/"), f"Incorrect original media: {image_url}"
                assert image_response.read(1), f"Empty original image: {image_url}"
    if route == "demo/detailflow/":
        assert document.forms == 0, "Public product sample has a data-collecting form"
        assert "Submitting inquiries is disabled" in html, "Demo submit gate missing"
        assert not document.scripts, "Demo loads unexpected external script"
        assert not document.css, "Demo loads unexpected external stylesheet"
    elif route in {"portfolio/facility-console/", "game-assets/"}:
        assert not document.css, "Portfolio must remain self-contained"
    elif route == "studio/":
        assert document.css == ["../assets/site.css", "../assets/inquiry.css"], "Studio inquiry stylesheets changed"
        assert document.scripts == ["../assets/inquiry.js"], "Studio copy-only inquiry script changed"
    else:
        assert len(document.css) == 1, f"Expected one stylesheet at {route}"
    for href in document.links + document.css + document.scripts:
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        target, _ = urldefrag(urljoin(page_url, href))
        if target.startswith("https://justicelinderman-creator.github.io/") and not target.startswith(BASE):
            raise AssertionError(f"Broken nested path: {href} on {route}")
        if target.startswith(BASE) and target not in checked:
            if Path(urlsplit(target).path).suffix.lower() in {".pdf", ".mp4", ".zip"}:
                suffix = Path(urlsplit(target).path).suffix.lower()
                expected_type = {".pdf": "application/pdf", ".mp4": "video/mp4", ".zip": "application/zip"}[suffix]
                with urlopen(Request(target, headers={"User-Agent": "NBM-Public-Site-Health/2.0"}), timeout=18) as response:
                    assert response.status == 200, f"Proof file missing: {target}"
                    content_type = response.headers.get("Content-Type", "")
                    allowed_types = (expected_type, "application/octet-stream", "application/x-zip-compressed") if suffix == ".zip" else (expected_type,)
                    assert any(content_type.startswith(value) for value in allowed_types), f"Incorrect media type: {target}"
                    prefix = response.read(2)
                    assert prefix, f"Empty proof or download file: {target}"
                    if suffix == ".zip":
                        assert prefix == b"PK", f"ZIP response is not an archive: {target}"
            else:
                load(target)
            checked.add(target)
    print("PASS", route or "/", "links", len(document.links),
          "css", len(document.css), "scripts", len(document.scripts))
print("PASS: public navigation, original portfolio media, safe draft store, consented email CTA and approved indexing.")

