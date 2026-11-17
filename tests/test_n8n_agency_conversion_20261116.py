"""Buyer-first n8n service: precise promise, evidence and a no-friction first contact."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from html.parser import HTMLParser
import unittest
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"services"/"n8n"/"index.html"
class Capture(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.headings=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a":self.links.append(a)
  if a.get("id"):self.ids.add(a["id"])
  if tag in ("h1","h2","h3"):self.headings.append(tag)
class AgencyBuyerTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=HTML.read_text(encoding="utf8")
  cls.markup=Capture();cls.markup.feed(cls.html)
 def test_free_fit_check_starts_without_mandatory_fields(self):
  links=[a for a in self.markup.links if a.get("id")=="quick-fit-check"]
  self.assertEqual(len(links),1)
  url=urlsplit(links[0]["href"])
  self.assertEqual(url.scheme,"mailto")
  self.assertEqual(url.path,"justice.linderman@gmail.com")
  params=parse_qs(url.query)
  self.assertIn("n8n lead-flow fit check",params["subject"][0].lower())
  self.assertIn("What breaks",params["body"][0])
  self.assertIn("No passwords",params["body"][0])
 def test_agency_value_and_precise_scope(self):
  for value in ("small agencies","n8n","lead","duplicate","$200","one existing workflow","one failure","written acceptance","rollback","free fit check"):
   self.assertIn(value.lower(),self.html.lower())
  self.assertIn("customer results are unverified",self.html.lower())
  for forbidden in ("guaranteed revenue","zero lost leads","100% uptime","proven client results","instant results"):
   self.assertNotIn(forbidden,self.html.lower())
 def test_verifiable_real_sample_is_named(self):
  self.assertIn("five recorded sandbox executions",self.html.lower())
  self.assertIn("synthetic data",self.html.lower())
  self.assertIn("not a paid client deployment",self.html.lower())
  self.assertIn('src="../proof/n8n-walkthrough.mp4"',self.html)
  self.assertTrue((ROOT/"services/proof/n8n-walkthrough.mp4").is_file())
 def test_existing_detailed_brief_and_privacy_remain(self):
  for value in ('id="brief"','id="failure"','id="issue"','id="expected"','id="open-email"','id="copy-email"','href="../../privacy.html"'):
   self.assertIn(value,self.html)
  self.assertNotIn("buy.stripe.com",self.html)
  self.assertNotIn("fetch(",self.html)
  self.assertNotIn("<form",self.html)
  self.assertEqual(self.markup.headings.count("h1"),1)
if __name__=="__main__":unittest.main()
