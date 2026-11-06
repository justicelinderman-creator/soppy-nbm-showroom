"""Execute the full site-health script against controlled deployment responses."""
from contextlib import redirect_stdout
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse,unquote
from unittest.mock import patch
import io,mimetypes,runpy,unittest

SITE=Path(__file__).resolve().parents[1]
SCRIPT=SITE/'scripts/site_health.py'
PREFIX='/soppy-nbm-showroom/'

class Clock:
    def __init__(self):self.now=0.;self.sleeps=[]
    def monotonic(self):return self.now
    def sleep(self,seconds):self.sleeps.append(seconds);self.now+=seconds

class Response:
    def __init__(self,body,content_type='text/plain'):
        # GitHub serves committed LF text; a Windows checkout may contain CRLF.
        self.body=body if content_type.startswith('image/') else body.replace(b'\r\n',b'\n')
        self.status=200;self.headers={'Content-Type':content_type}
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,size=-1):return self.body if size<0 else self.body[:size]

class Deployment:
    def __init__(self,clock,route=None,until=0,kind='wrong',request_seconds=0):
        self.clock=clock;self.route=route;self.until=until;self.kind=kind
        self.request_seconds=request_seconds;self.requests=[]
    def response(self,url,timeout=18):
        parsed=urlparse(url)
        if not parsed.path.startswith(PREFIX):raise AssertionError('Test attempted an unexpected destination: '+url)
        route=unquote(parsed.path[len(PREFIX):]);path=SITE/(route+'index.html' if not route or route.endswith('/') else route)
        assert path.resolve().is_relative_to(SITE.resolve())
        self.requests.append({'route':route,'query':parsed.query,'timeout':timeout,'at':self.clock.now})
        self.clock.now+=min(self.request_seconds,timeout)
        if self.kind=='network_timeout':raise TimeoutError('Controlled deployment connection timeout')
        if route==self.route and self.clock.now<self.until:
            if self.kind=='404':raise HTTPError(url,404,'Not published yet',None,None)
            if self.kind=='invalid_utf8':return Response(b'\xff\xfe')
            if self.kind=='old_studio':
                data=path.read_bytes().replace(b'<link rel="stylesheet" href="../assets/inquiry.css">',b'').replace(b'<script src="../assets/inquiry.js" defer></script>',b'')
                return Response(data,'text/html')
            if self.kind=='old_core':return Response(path.read_bytes().replace(b'content="index,follow"',b'content="noindex"'),'text/html')
            if self.kind=='unsafe_store':return Response(path.read_bytes().replace(b'Checkout not active',b'Checkout changed'),'text/html')
            return Response(b'Wrong or stale asset, despite HTTP 200')
        if not path.is_file():raise HTTPError(url,404,'Fixture route not found',None,None)
        return Response(path.read_bytes(),mimetypes.guess_type(path.name)[0] or 'text/plain')
    def urlopen(self,request,timeout=18):return self.response(request.full_url,timeout)

def run_health(route=None,until=0,kind='wrong',request_seconds=0,script=SCRIPT):
    clock=Clock();server=Deployment(clock,route,until,kind,request_seconds);stdout=io.StringIO();error=None
    with patch('urllib.request.urlopen',side_effect=server.urlopen),patch('time.monotonic',side_effect=clock.monotonic),patch('time.sleep',side_effect=clock.sleep),redirect_stdout(stdout):
        try:runpy.run_path(str(script),run_name='__main__')
        except Exception as exc:error={'type':type(exc).__name__,'message':str(exc)}
    return {'error':error,'elapsed':clock.now,'sleeps':clock.sleeps,'requests':server.requests,'stdout':stdout.getvalue()}

class DeploymentReadinessTests(unittest.TestCase):
    def success(self,result):
        self.assertIsNone(result['error'],result)
        self.assertEqual(sum(line.startswith('PASS ') for line in result['stdout'].splitlines()),11)
        self.assertIn('PASS: public navigation',result['stdout'])
    def expired(self,result):
        self.assertIsNotNone(result['error'],result)
        self.assertEqual(result['error']['type'],'AssertionError')
        self.assertIn('did not finish publishing',result['error']['message'])
        self.assertLessEqual(result['elapsed'],90)
        self.assertNotIn('PASS ',result['stdout'])
    def test_current_release_passes_without_sleep(self):
        r=run_health();self.success(r);self.assertEqual(r['sleeps'],[])
    def test_old_studio_waits_for_current_page(self):
        r=run_health('studio/',10,'old_studio');self.success(r);self.assertEqual(r['elapsed'],10)
    def test_missing_inquiry_css_recovers_after_publication(self):
        r=run_health('assets/inquiry.css',10,'404');self.success(r);self.assertEqual(r['elapsed'],10)
    def test_missing_inquiry_script_recovers_after_publication(self):
        r=run_health('assets/inquiry.js',10,'404');self.success(r);self.assertEqual(r['elapsed'],10)
    def test_stale_radar_script_waits_for_reviewed_content(self):
        r=run_health('creatorops/checker/radar.js',10);self.success(r);self.assertEqual(r['elapsed'],10)
    def test_http_200_wrong_assets_do_not_pass(self):
        for route in ['assets/inquiry.css','assets/inquiry.js','creatorops/checker/radar.js']:
            with self.subTest(route=route):self.expired(run_health(route,1000))
    def test_permanently_old_studio_fails_within_budget(self):
        self.expired(run_health('studio/',1000,'old_studio'))
    def test_prior_core_readiness_checks_are_preserved(self):
        r=run_health('free/',10,'old_core');self.success(r);self.assertEqual(r['elapsed'],10)
    def test_invalid_asset_encoding_is_not_accepted(self):
        self.expired(run_health('assets/inquiry.js',1000,'invalid_utf8'))
    def test_network_timeouts_consume_the_remaining_budget(self):
        r=run_health(kind='network_timeout',request_seconds=18);self.expired(r)
        self.assertTrue(all(0<x['timeout']<=18 for x in r['requests']))
    def test_publication_just_before_deadline_can_pass(self):
        r=run_health('studio/',85,'old_studio');self.success(r);self.assertEqual(r['elapsed'],85)
    def test_publication_at_deadline_does_not_extend_budget(self):
        self.expired(run_health('studio/',90,'old_studio'))
    def test_unrelated_health_failures_remain_failures(self):
        r=run_health('store/',1000,'unsafe_store')
        self.assertEqual(r['error']['message'],'Store checkout gate missing')
        self.assertEqual(r['sleeps'],[])
    def test_request_timeout_is_capped_by_remaining_budget(self):
        r=run_health('assets/inquiry.js',1000,request_seconds=8);self.expired(r)
        self.assertTrue(all(x['timeout']<=90-x['at'] for x in r['requests']))
        self.assertTrue(any(x['timeout']<18 for x in r['requests']))

if __name__=='__main__':unittest.main()
