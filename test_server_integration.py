import sys, json, threading, tempfile, unittest, urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import server, test_discovery as T

SCAM_PAGE = T.PAGES['https://scamhack.example.com/join'][1]

def fake_http_json(url, payload, headers=None, timeout=45):
    if 'tavily.com/extract' in url: return {'results': [{'raw_content': SCAM_PAGE * 2}]}
    if 'generativelanguage' in url:
        return {'candidates': [{'content': {'parts': [{'text': json.dumps({'summary': 's', 'registration_fee': 'Free', 'deadline': '2026-12-01', 'organizer': 'Fast Prize Team',
                'red_flags': [], 'positive_signals': [], 'missing_information': [], 'recommendation': 'Review'})}]}}]}
    raise RuntimeError('unexpected call ' + url)

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.DB = Path(tempfile.mkdtemp()) / 't.db'; server.TAVILY = 'x'; server.GEMINI = 'g'; server.OPENAI = ''; server.INVITE_CODE='test-invite'; server.ADMIN_DASHBOARD_KEY='test-admin'; server.SESSION_SECRET='test-secret-for-unit-tests-32-bytes'; server.DAILY_ACTION_LIMIT=100
        server.tavily_search = T.fake_search; server.llm_json = T.fake_llm
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler); cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(cls): cls.httpd.shutdown()
    def call(self, path, body=None):
        req = urllib.request.Request(f'http://127.0.0.1:{self.port}{path}', data=json.dumps(body).encode() if body is not None else None, headers={'Content-Type': 'application/json', 'Cookie': 'ap_session='+server._sign_token('invite')})
        try:
            with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e: return e.code, json.loads(e.read())
    def test_flow(self):
        # NOTE: discovery uses TODAY=real date; fake pages carry 2026 dates, so pin "today" through the module default
        import datetime, discovery
        orig = discovery.datetime.date
        class FakeDate(datetime.date):
            @classmethod
            def today(cls): return T.TODAY
        discovery.datetime.date = FakeDate; server.datetime.date = FakeDate
        try:
            st, data = self.call('/api/search', {'query': 'free online AI hackathon for beginners', 'city': '', 'fee': 'All', 'mode': 'All'})
            self.assertEqual(st, 200); self.assertGreaterEqual(data['count'], 2)
            self.assertIn('requirements', data); self.assertIn('diagnostics', data); self.assertIn('AI/ML', data['requirements']['themes'])
            top = data['items'][0]; self.assertEqual(top['title'], 'AI for Good Hackathon 2026'); self.assertIn('matchReasons', top)
            # cached results must come back (previously serial_op() dropped every record)
            st, cached = self.call('/api/opportunities'); self.assertEqual(st, 200); self.assertEqual(len(cached['items']), data['count'])
            self.assertTrue(all(i['sourceType'] == 'Cached live result' for i in cached['items']))
            # eligibility no longer 500s on cache lookups (OPENAI missing -> clean 400)
            st, _ = self.call('/api/eligibility', {'opportunityId': top['id']}); self.assertEqual(st, 400)
            # ScamShield scan merges evidence-quoted deterministic checks and challenges the AI's own claims
            scam = [i for i in data['items'] if 'Mega Cash' in i['title']][0]
            orig_h = server.http_json; server.http_json = fake_http_json
            try: st, scan = self.call('/api/scan', {'opportunityId': scam['id']})
            finally: server.http_json = orig_h
            self.assertEqual(st, 200, scan)
            self.assertTrue(any('scam123@ybl' in x for x in scan['red_flags']), scan['red_flags'])
            self.assertTrue(any('not found in the fetched page text' in x for x in scan['missing_information']))   # AI said 2026-12-01; page says 30 Dec
            self.assertTrue(any('reported the event as free' in x for x in scan['missing_information']))
            self.assertTrue(scan['verification']['highRisk'])
            # filters travel to the server
            st, d2 = self.call('/api/search', {'query': 'hackathon', 'fee': 'Free', 'mode': 'In-person'})
            self.assertFalse(any(i['fee'] == 'Fee required' or i['mode'] == 'Online' for i in d2['items']))
        finally:
            discovery.datetime.date = orig; server.datetime.date = orig
    def test_static(self):
        with urllib.request.urlopen(f'http://127.0.0.1:{self.port}/') as r: html = r.read().decode()
        self.assertIn('id="unlock"', html)
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/',headers={'Cookie':'ap_session='+server._sign_token('invite')})
        with urllib.request.urlopen(req) as r: app_html=r.read().decode()
        self.assertIn('id="modeFilter"', app_html); self.assertIn('id="searchInsight"', app_html)


    def test_invite_gate_and_unlock(self):
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/api/profile')
        try:
            urllib.request.urlopen(req)
            self.fail('protected API unexpectedly allowed')
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code,401)
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/api/auth/unlock',data=json.dumps({'code':'wrong'}).encode(),headers={'Content-Type':'application/json'})
        try: urllib.request.urlopen(req); self.fail('wrong invite code unexpectedly accepted')
        except urllib.error.HTTPError as e: self.assertEqual(e.code,403)
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/api/auth/unlock',data=json.dumps({'code':'test-invite'}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req) as r:
            self.assertEqual(r.status,200); self.assertIn('ap_session=',r.headers.get('Set-Cookie',''))

    def test_three_action_rolling_quota(self):
        original_limit=server.DAILY_ACTION_LIMIT; original_live=server.live_search
        try:
            server.DAILY_ACTION_LIMIT=3
            c=server.db(); c.execute('DELETE FROM daily_usage'); c.commit(); c.close()
            server.live_search=lambda *a,**k:{'items':[],'requirements':{},'diagnostics':{}}
            for _ in range(3):
                st,_=self.call('/api/search',{'query':'test hackathon','city':'','fee':'All','mode':'All'})
                self.assertEqual(st,200)
            st,limited=self.call('/api/search',{'query':'test hackathon','city':'','fee':'All','mode':'All'})
            self.assertEqual(st,429); self.assertIn('retryAt',limited)
        finally:
            server.DAILY_ACTION_LIMIT=original_limit; server.live_search=original_live

    def test_admin_gate(self):
        st, data=self.call('/api/admin/stats')
        self.assertEqual(st,401)
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}/api/admin/stats',headers={'Cookie':'ap_admin='+server._sign_token('admin')})
        with urllib.request.urlopen(req) as r: stats=json.loads(r.read())
        self.assertIn('uniqueVisitors24h',stats)


if __name__ == '__main__': unittest.main(verbosity=2)
