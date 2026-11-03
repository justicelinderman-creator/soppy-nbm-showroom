"""Safety contract for public Roblox Studio Companion research and beta-interest page.

No network calls, no marketplace listing and no third-party personal data.
"""
import unittest
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://justicelinderman-creator.github.io/soppy-nbm-showroom"
class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes=[];self.links=[];self.metas={};self.canonical=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.nodes.append(tag)
        if tag=="a":self.links.append(d.get("href",""))
        if tag=="meta" and d.get("name"):self.metas[d["name"]]=d.get("content","")
        if tag=="link" and d.get("rel")=="canonical":self.canonical.append(d.get("href"))

class CompanionResearchPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"creatorops/index.html").read_text(encoding="utf8")
        cls.parser=Tags();cls.parser.feed(cls.html)
    def test_indexing_and_canonical(self):
        self.assertEqual(self.parser.metas.get("robots"),"index,follow")
        self.assertEqual(self.parser.canonical,[BASE+"/creatorops/"])
    def test_preview_not_fake_sale(self):
        for snippet in ("NOT AVAILABLE FOR DOWNLOAD","Native Studio trial pending","no downloadable beta","no paid","one Studio Undo","one-to-one inquiry"):
            self.assertIn(snippet.lower(),self.html.lower())
    def test_preview_workflow_is_honest(self):
        for snippet in ("ShipCheck","QuickOps","200","Preview","Undo","script","does not"):
            self.assertIn(snippet.lower(),self.html.lower())
    def test_no_payment_or_active_install(self):
        self.assertFalse(any(x in self.parser.nodes for x in ("form","input","iframe","script","button")))
        for bad in ("stripe.com","paypal.com","checkout.","formspree","onclick=","fetch(","Download plugin","install now"):
            self.assertNotIn(bad.lower(),self.html.lower())
    def test_user_initiated_email_is_only_data_route(self):
        mails=[x for x in self.parser.links if x.startswith("mailto:")]
        self.assertEqual(len(mails),3)
        self.assertTrue(all(x.startswith("mailto:justice.linderman@gmail.com?subject=Cosie%20Studio%20Companion%20Beta%20Interest") for x in mails))
    def test_no_private_source_leaked(self):
        for bad in (".rbxmx",".blend",".fbx",".glb","github.com/justicelinderman-creator/ECHO_ROBLOX_STUDIOS","api_key","customer testimonial"):
            self.assertNotIn(bad.lower(),self.html.lower())
    def test_real_service_and_free_audit_unmodified(self):
        studio=(ROOT/"studio/index.html").read_text(encoding="utf8")
        free=(ROOT/"free/index.html").read_text(encoding="utf8")
        self.assertIn("$750",studio)
        self.assertIn("mailto:justice.linderman@gmail.com",studio)
        self.assertIn('content="index,follow"',free)
        self.assertIn("12-point",free.lower())
    def test_navigation_links(self):
        self.assertTrue(all(link in self.parser.links for link in ("../studio/","../portfolio/facility-console/","../free/","../privacy.html")))
        for path in ("index.html","studio/index.html","portfolio/facility-console/index.html"):
            self.assertIn("creatorops/",(ROOT/path).read_text(encoding="utf8"))
    def test_sitemap_only_current_public_education(self):
        tree=ET.parse(ROOT/"sitemap.xml")
        loc=[e.text for e in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(loc,[BASE+"/free/",BASE+"/studio/",BASE+"/portfolio/facility-console/",BASE+"/creatorops/"])
    def test_store_still_noindex(self):
        self.assertIn('content="noindex,nofollow"',(ROOT/"store/index.html").read_text(encoding="utf8"))
    def test_privacy_beta_email_notice(self):
        self.assertIn("Cosie Studio Companion beta interest",(ROOT/"privacy.html").read_text(encoding="utf8"))
    def test_no_independent_purchase_or_testimonials(self):
        self.assertIn("not a recorded screenshot",self.html)
        self.assertIn("No claimed time savings",self.html)
        self.assertIn("no checkout",self.html.lower())
if __name__=="__main__":unittest.main()
