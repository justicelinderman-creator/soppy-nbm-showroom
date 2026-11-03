"""Public first-buyer discovery launch: read-only static contract. No network or customer data."""
from pathlib import Path
from html.parser import HTMLParser
import unittest,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE="https://justicelinderman-creator.github.io/soppy-nbm-showroom"
class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.images=[];self.meta={};self.canon=[];self.tags=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.tags.append(tag)
        if tag=="a": self.links.append(d.get("href",""))
        if tag=="img": self.images.append(d)
        if tag=="meta" and d.get("name"):self.meta[d["name"]]=d.get("content","")
        if tag=="link" and d.get("rel")=="canonical":self.canon.append(d.get("href"))
class LaunchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages={}
        for name,p in {"studio":"studio/index.html","portfolio":"portfolio/facility-console/index.html","home":"index.html","free":"free/index.html"}.items():
            f=ROOT/p
            if not f.exists() and name=="free":continue
            content=f.read_text(encoding="utf8");parser=Tags();parser.feed(content)
            cls.pages[name]=(content,parser)
    def test_exact_discovery(self):
        for name in ("studio","portfolio"):
            text,page=self.pages[name]
            self.assertEqual(page.meta.get("robots"),"index,follow")
            self.assertEqual(page.canon,[BASE+("/studio/" if name=="studio" else "/portfolio/facility-console/")])
    def test_prelaunch_store_not_indexed(self):
        self.assertEqual(self.pages["home"][1].meta.get("robots"),"noindex,nofollow")
        store=ROOT/"store/index.html"
        if store.exists():
            p=Tags();p.feed(store.read_text(encoding="utf8"))
            self.assertEqual(p.meta.get("robots"),"noindex,nofollow")
    def test_portfolio_images_referenced(self):
        t,p=self.pages["portfolio"]
        self.assertEqual(len(p.images),3)
        folder=ROOT/"portfolio/facility-console"
        for image in p.images:
            self.assertTrue((folder/image["src"]).is_file())
            self.assertTrue(image.get("alt"))
        self.assertTrue((folder/"COSIE_CONSOLE_PORTFOLIO_CARD.jpg").is_file())
    def test_original_truth(self):
        t,_=self.pages["portfolio"]
        for text in ("10,512","90","11","0","independently","not","speculative"):
            self.assertIn(text.lower(),t.lower())
        self.assertNotIn("guaranteed revenue",t.lower())
    def test_portfolio_contact_and_privacy(self):
        t,p=self.pages["portfolio"]
        self.assertEqual(len([x for x in p.links if x.startswith("mailto:justice.linderman@gmail.com")]),2)
        self.assertIn("../../privacy.html",p.links)
        self.assertIn("../../studio/",p.links)
        self.assertNotIn("automatic price quotation",t.lower().replace("no automatic price quotation",""))
    def test_no_live_forms_or_checkout(self):
        for key in ("portfolio","studio"):
            t,p=self.pages[key]
            for tag in ("form","input","iframe","script"):
                self.assertNotIn(tag,p.tags,(key,tag))
            for expr in ("stripe.com","paypal.com","formspree","fetch(","onclick="):
                self.assertNotIn(expr,t.lower())
    def test_main_and_studio_link_portfolio(self):
        for key in ("studio","home"):
            t,p=self.pages[key]
            self.assertIn("../portfolio/facility-console/" if key=="studio" else "./portfolio/facility-console/",p.links)
    def test_real_portfolio_has_no_source_download(self):
        p=ROOT/"portfolio/facility-console"
        self.assertTrue(all(q.suffix.lower() not in (".blend",".fbx",".glb",".rbxl",".rbxm",".luau") for q in p.iterdir() if q.is_file()))
    def test_sitemap_exact_urls(self):
        tree=ET.parse(ROOT/"sitemap.xml")
        locations=[t.text for t in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(locations,[BASE+"/free/",BASE+"/studio/",BASE+"/portfolio/facility-console/"])
        self.assertEqual(len(set(locations)),3)
    def test_no_outbound_marketing(self):
        for key in ("portfolio","studio"):
            t,p=self.pages[key]
            self.assertNotIn("newsletter subscription",t.lower())
            self.assertFalse(any("checkout" in a.lower() for a in p.links))
if __name__=="__main__":unittest.main()
