"""Static guardrails for the real email-only NBM Studio offer. No network or buyer data."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "studio" / "index.html"
README = ROOT / "docs" / "nbm-sales-funnel-v1.md"


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.elements = []
        self.links = []
        self.ids = set()
        self.metas = {}
        self.headings = []
        self.disabled_ctas = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "meta" and attrs.get("name"):
            self.metas[attrs["name"].lower()] = attrs.get("content", "").lower()
        if tag == "span" and attrs.get("aria-disabled") == "true":
            self.disabled_ctas += 1
        if tag == "h1":
            self.headings.append(tag)


class StudioPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = STUDIO.read_text(encoding="utf-8")
        cls.parser = Tags()
        cls.parser.feed(cls.html)

    def test_owner_approved_studio_indexing(self):
        self.assertEqual(self.parser.metas.get("robots"), "index,follow")
        self.assertIn("https://justicelinderman-creator.github.io/soppy-nbm-showroom/studio/", self.html)
        self.assertIn("PROJECT INQUIRIES OPEN BY EMAIL", self.html)
        self.assertIn("No online checkout", self.html)

    def test_no_collection_or_checkout(self):
        for tag in ("form", "input", "select", "iframe"):
            self.assertNotIn(tag, self.parser.tags, f"Unexpected active element: {tag}")
        # Read-only copy controls do not collect or submit visitor data.
        scripts = [attrs for tag, attrs in self.parser.elements if tag == "script"]
        self.assertEqual([s.get("src") for s in scripts], ["../assets/inquiry.js"])
        textareas = [attrs for tag, attrs in self.parser.elements if tag == "textarea"]
        self.assertEqual(len(textareas), 3)
        self.assertTrue(all("readonly" in attrs and "name" not in attrs for attrs in textareas))
        buttons = [attrs for tag, attrs in self.parser.elements if tag == "button"]
        self.assertEqual(len(buttons), 3)
        self.assertTrue(all(attrs.get("type") == "button" and attrs.get("data-copy-target") for attrs in buttons))
        copy_script = (ROOT / "assets/inquiry.js").read_text(encoding="utf-8")
        for api in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "window.open", "location."):
            self.assertNotIn(api, copy_script)
        for value in ("tel:", "https://checkout.", "stripe.com", "paypal.com", "formspree", "onclick=", "fetch(", "localStorage"):
            self.assertNotIn(value.lower(), self.html.lower())
        self.assertEqual(self.parser.disabled_ctas, 0)
        self.assertEqual(sum(h.startswith("mailto:") for h in self.parser.links), 3)
        self.assertIn("justice.linderman@gmail.com", self.html)
        self.assertIn("not an on-site form", self.html.lower())

    def test_offer_consistent(self):
        for value in (
            "$750",
            "Up to three service sections",
            "Two consolidated revision rounds",
            "end-to-end test",
            "written agreement",
            "Hosting",
            "No promise of increased bookings",
        ):
            self.assertIn(value.lower(), self.html.lower())
        self.assertTrue(README.exists())

    def test_navigation_and_accessibility(self):
        self.assertEqual(self.parser.tags.count("main"), 1)
        self.assertEqual(len(self.parser.headings), 1)
        self.assertIn('aria-current="page"', self.html)
        self.assertEqual(self.parser.tags.count("link"), 3)
        self.assertEqual([attrs.get("href") for tag,attrs in self.parser.elements if tag=="link" and attrs.get("rel")=="stylesheet"], ["../assets/site.css", "../assets/inquiry.css"])
        self.assertNotIn("http://", self.html)
        self.assertIn("../demo/detailflow/", self.parser.links)
        self.assertIn("../free/", self.parser.links)
        self.assertIn("../privacy.html", self.parser.links)
        for href in self.parser.links:
            if href.startswith("#"):
                self.assertIn(href[1:], self.parser.ids, f"Missing internal target: {href}")
        self.assertTrue(re.search(r'<a[^>]*href="#pilot"', self.html))


if __name__ == "__main__":
    unittest.main()
