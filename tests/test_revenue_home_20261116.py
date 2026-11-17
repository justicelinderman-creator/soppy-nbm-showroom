"""Revenue homepage CTA contract: buyer-facing route, no public checkout."""
from pathlib import Path
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self):
  super().__init__()
  self.anchors=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":self.anchors.append(dict(attrs))
class RevenueHome(unittest.TestCase):
 def test_n8n_buyer_path_is_prominent_and_accurate(self):
  html=(ROOT/"index.html").read_text(encoding="utf8")
  p=Links();p.feed(html)
  assert any(a.get("href")=="./services/n8n/" for a in p.anchors),"Missing direct $200 n8n buyer route"
  self.assertIn("Fix an n8n workflow",html)
  self.assertIn("$200 scoped pilot",html)
  self.assertIn("Scope agreed before payment",html)
 def test_no_open_payment_or_form_on_home(self):
  html=(ROOT/"index.html").read_text(encoding="utf8").lower()
  for unsafe in ("buy.stripe.com","checkout.stripe.com","<form","guaranteed roi","guaranteed earnings"):
   self.assertNotIn(unsafe,html)
  self.assertIn('href="./privacy.html"',html)
  self.assertIn('href="./services/"',html)
 def test_public_route_and_sitemap_agree(self):
  content=(ROOT/"sitemap.xml").read_text(encoding="utf8")
  self.assertIn("soppy-nbm-showroom/services/n8n/",content)
  self.assertIn("soppy-nbm-showroom/</loc>",content)
if __name__=="__main__":
 unittest.main()
