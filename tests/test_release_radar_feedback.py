"""Contract for the opt-in, privacy-preserving Release Radar feedback prompt."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

R=Path(__file__).resolve().parents[1]
HTML=(R/'creatorops/checker/index.html').read_text(encoding='utf8')
class AnchorParser(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self.tags=[]
 def handle_starttag(self,tag,attrs):
  self.tags.append(tag)
  if tag=='a':self.links.append(dict(attrs))

class Feedback(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=AnchorParser();cls.p.feed(HTML)
  cls.link=next((x for x in cls.p.links if x.get('href','').startswith(
   'mailto:justice.linderman@gmail.com?subject=Cosie%20Release%20Radar%20Feedback')
   and x.get('href','').find('body=')>=0),None)
 def test_explicit_opt_in_link(self):
  self.assertIsNotNone(self.link)
 def test_feedback_only_shows_with_results(self):
  self.assertLess(HTML.index('id="results"'),HTML.index('id="feedback"'))
  self.assertLess(HTML.index('id="feedback"'),HTML.index('</section>',HTML.index('id="results"')))
 def test_three_quality_questions(self):
  href=self.link['href']
  for phrase in ('What%20helped','What%20was%20confusing%20or%20wrong',
                 'Would%20you%20recommend'):
   self.assertIn(phrase,href)
 def test_no_game_file_or_report_in_mailto(self):
  href=self.link['href'].lower()
  for term in ('file=', 'attachment=', 'json=', 'source=', 'data:', 'credentials='):
   self.assertNotIn(term,href)
  self.assertIn('private%20game%20files',href)
 def test_no_signup_form_or_autosend(self):
  self.assertNotIn('form',self.p.tags)
  self.assertNotIn('iframe',self.p.tags)
  self.assertNotIn('onclick=',HTML.lower())
  self.assertNotIn('fetch(',HTML)
 def test_existing_free_demo_and_export_preserved(self):
  self.assertIn('id="demo"',HTML)
  self.assertIn('id="download"',HTML)
  self.assertIn('id="placeFile"',HTML)
 def test_no_subscription_or_purchase(self):
  self.assertIn('No sign-up, tracking, payments',HTML)
  self.assertIn("not available for purchase",HTML.lower())
if __name__=='__main__':unittest.main()
