"""Release Radar source and privacy contract, no network or customer files."""
import unittest
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.tags=[];self.links=[];self.scripts=[];self.metas={};self.inputs=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.tags.append(tag)
        if tag=="a":self.links.append(d.get("href",""))
        if tag=="script":self.scripts.append(d.get("src",""))
        if tag=="input":self.inputs.append(d)
        if tag=="meta":self.metas[d.get("name")]=d.get("content","")
class RadarContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"creatorops/checker/index.html").read_text(encoding="utf8")
        cls.engine=(ROOT/"creatorops/checker/engine.js").read_text(encoding="utf8")
        cls.ui=(ROOT/"creatorops/checker/radar.js").read_text(encoding="utf8")
        cls.p=Tags();cls.p.feed(cls.html)
    def test_public_page_not_fake_commerce(self):
        self.assertIn("no checkout",self.html.lower())
        self.assertIn("not available for purchase",self.html.lower())
    def test_file_stays_local(self):
        self.assertIn("No uploads",self.html)
        self.assertIn("connect-src 'none'",self.html)
        self.assertIn("LOCAL_BROWSER_ONLY",self.engine)
    def test_only_two_local_scripts(self):
        self.assertEqual(self.p.scripts,["./engine.js","./radar.js"])
        self.assertNotIn("iframe",self.p.tags)
        self.assertNotIn("form",self.p.tags)
    def test_no_network_or_persistent_storage(self):
        combined=self.engine+self.ui
        for forbidden in ("fetch(","XMLHttpRequest","WebSocket(","sendBeacon(","localStorage","sessionStorage","HttpService:","document.cookie","eval("):
            self.assertNotIn(forbidden,combined)
    def test_report_display_uses_text_nodes(self):
        self.assertIn("textContent",self.ui)
        self.assertIn("replaceChildren()",self.ui)
        self.assertNotIn("innerHTML",self.ui)
    def test_local_json_not_raw_xml_export(self):
        self.assertIn("JSON.stringify(current,null,2)",self.ui)
        self.assertNotIn("new Blob([xml",self.ui)
    def test_roblox_xml_supported_binary_rejected(self):
        self.assertIn(".rbxlx,.rbxmx",self.html)
        self.assertIn("Binary .rbxl",self.html)
        self.assertIn("12 MB",self.html)
    def test_transparent_physics_and_interaction_rules(self):
        for rule in ("INVISIBLE_SOLID","INVALID_SIZE","LARGE_UNANCHORED","PROMPT_ZERO_RANGE","PARTICLE_HIGH_RATE","WIDE_BRIGHT_LIGHT"):
            self.assertIn(rule,self.engine)
    def test_no_auto_edits_or_script_inspection(self):
        self.assertIn("counts.scripts++;continue",self.engine)
        self.assertNotIn('property(item,"Source")',self.engine)
        self.assertNotIn("SetAttribute",self.engine)
        self.assertNotIn("Instance.new",self.engine)
    def test_indexable_and_sitemap_linked(self):
        self.assertEqual(self.p.metas.get("robots"),"index,follow")
        self.assertIn('rel="canonical"',self.html)
        self.assertIn("creatorops/checker/",(ROOT/"sitemap.xml").read_text(encoding="utf8"))
        self.assertIn('./checker/',(ROOT/"creatorops/index.html").read_text(encoding="utf8"))
    def test_file_input_and_demo(self):
        self.assertEqual(len([x for x in self.p.inputs if x.get("type")=="file"]),1)
        for name in ("placeFile","demo","download","reset","search","filter","results","status"):
            self.assertIn('id="'+name+'"',self.html)
    def test_demo_is_identified_as_synthetic(self):
        self.assertIn("Synthetic example",self.ui)
    def test_no_user_tracking_or_hidden_checkout(self):
        for keyword in ("stripe.com","paypal.com","formspree","google-analytics.com","googletagmanager","buy now","download plugin"):
            self.assertNotIn(keyword,self.html.lower())
    def test_existing_store_stays_unindexed(self):
        self.assertIn('content="noindex,nofollow"',(ROOT/"store/index.html").read_text(encoding="utf8"))
    def test_sources_document_real_limitations(self):
        self.assertIn("cannot measure FPS",self.html)
        self.assertIn("does not inspect script",self.html.lower())
        self.assertIn("No uploads",self.html)
if __name__=="__main__":unittest.main()
