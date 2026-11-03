"""Static safety and funnel checks for indexable free audit -> optional email inquiry."""
from pathlib import Path
from html.parser import HTMLParser
import unittest
R=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.inputs=[]; self.ids=set(); self.meta={}
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a":self.links.append(d.get("href",""))
        if tag=="input":self.inputs.append(d)
        if d.get("id"):self.ids.add(d["id"])
        if tag=="meta" and d.get("name"):self.meta[d["name"]]=d.get("content","")
class AuditInboundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(R/"free"/"index.html").read_text(encoding="utf8")
        cls.js=(R/"free"/"audit.js").read_text(encoding="utf8")
        cls.page=Page(); cls.page.feed(cls.html)
    def test_existing_free_audit_preserved(self):
        self.assertEqual(len([i for i in self.page.inputs if i.get("type")=="checkbox"]),12)
        for v in ("audit-score","audit-fill","audit-priority","copy-audit","reset-audit","audit-manual"):
            self.assertIn(v,self.page.ids)
        self.assertIn('src="audit.js"',self.html)
        self.assertEqual(self.page.meta.get("robots"),"index,follow")
    def test_optional_human_initiated_email(self):
        matches=[l for l in self.page.links if l.startswith("mailto:")]
        self.assertEqual(matches,["mailto:justice.linderman@gmail.com?subject=NBM%20Free%20Audit%20Project%20Inquiry"])
        self.assertIn("never automatically emailed or uploaded",self.html.lower())
        self.assertIn("../privacy.html",self.page.links)
        self.assertIn("../studio/",self.page.links)
    def test_no_tracking_or_automatic_submission(self):
        for keyword in ("<form","stripe.com","paypal.com","formspree","checkout.","fetch(","XMLHttpRequest","sendBeacon","localStorage"):
            self.assertNotIn(keyword.lower(),(self.html+"\n"+self.js).lower())
        self.assertIn("Generated locally in the browser",self.js)
    def test_no_fake_performance_claim(self):
        self.assertIn("No guaranteed results",self.html)
        self.assertIn("proposed $750 website pilot",self.html)
if __name__=="__main__":unittest.main()
