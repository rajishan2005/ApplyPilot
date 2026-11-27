import sys, unittest, datetime, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import discovery as D

TODAY = datetime.date(2026, 11, 27)

# ---- fake web: url -> (title, page text, what the "LLM" extracts) -------------------------------
PAGES = {
 'https://aiforgood.devpost.com/?utm_source=x': ('AI for Good Hackathon 2026 | Devpost',
   'AI for Good Hackathon 2026. Organized by GreenTech Labs. Online hackathon open to students worldwide. Registration is free. Prizes: $5,000 in cash. '
   'Registration deadline: December 20, 2026. Beginner friendly - all skill levels welcome. Contact: team@greentechlabs.org. Build with machine learning and LLMs.',
   {'is_single_event': True, 'title': 'AI for Good Hackathon 2026', 'organizer': 'GreenTech Labs', 'type': 'Hackathon', 'mode': 'Online', 'city': 'Online',
    'registration_deadline': '2026-12-20', 'fee': 'Free', 'registration_fee': 'Not stated', 'compensation': '$5,000 in cash', 'eligibility': 'Students', 'skills': ['Python'], 'themes': ['AI'],
    'official_website': 'https://greentechlabs.org'}),
 'https://unstop.com/hackathons/ai-for-good-hackathon-2026-123456': ('AI for Good Hackathon 2026 - Unstop',
   'AI for Good Hackathon 2026 by GreenTech Labs. Register now. Last date to register: 20 Dec 2026. No registration fee. Official site https://greentechlabs.org online event.',
   {'is_single_event': True, 'title': 'AI for Good Hackathon 2026', 'organizer': 'GreenTech Labs', 'type': 'Hackathon', 'mode': 'Online', 'registration_deadline': '2026-12-20', 'fee': 'Free'}),
 'https://devpost.com/hackathons': ('Find hackathons | Devpost', 'list of hackathons', {'is_single_event': False, 'type': 'Hackathon'}),
 'https://unstop.com/hackathons': ('Hackathons - Unstop', 'many hackathons', {'is_single_event': False, 'type': 'Hackathon'}),
 'https://devfolio.co/hackathons': ('Hackathons on Devfolio', 'many', {'is_single_event': False, 'type': 'Hackathon'}),
 'https://oldhack.devpost.com': ('OldHack 2023 | Devpost', 'ended', {'is_single_event': True, 'type': 'Hackathon', 'title': 'OldHack 2023'}),
 'https://expired.devfolio.co': ('Expired Hack 2026', 'Expired Hack 2026 by Foo Club. Registration deadline: 1 October 2026. Offline in Bengaluru.',
   {'is_single_event': True, 'title': 'Expired Hack 2026', 'organizer': 'Foo Club', 'type': 'Hackathon', 'registration_deadline': '2026-10-01', 'mode': 'In-person', 'city': 'Bengaluru'}),
 'https://halluc.devfolio.co': ('Halluc Hack 2026', 'Halluc Hack 2026 hosted by Zed Society. Applications open soon. Venue: Pune campus. In-person.',
   {'is_single_event': True, 'title': 'Halluc Hack 2026', 'organizer': 'Zed Society', 'type': 'Hackathon', 'registration_deadline': '2026-12-31', 'mode': 'In-person', 'city': 'Pune', 'fee': 'Free'}),
 'https://blr.devfolio.co': ('BLR Build Hack 2026', 'BLR Build Hack 2026 by Bengaluru Dev Society. Offline at Koramangala, Bengaluru. Registration deadline: 5 January 2027. '
   'Registration fee: Rs. 500 per team. Build web apps with JavaScript and React. Prizes: Rs. 1,00,000.',
   {'is_single_event': True, 'title': 'BLR Build Hack 2026', 'organizer': 'Bengaluru Dev Society', 'type': 'Hackathon', 'registration_deadline': '2027-01-05', 'mode': 'In-person', 'city': 'Bengaluru',
    'fee': 'Fee required', 'registration_fee': 'Rs. 500', 'compensation': 'Rs. 1,00,000', 'skills': ['JavaScript', 'React'], 'themes': ['Web']}),
 'https://scamhack.example.com/join': ('Mega Cash Hackathon 2026', 'Mega Cash Hackathon 2026 by Fast Prize Team. Hurry only 10 seats left! Pay Rs 999 to scam123@ybl. Registration deadline: 30 December 2026. Online.',
   {'is_single_event': True, 'title': 'Mega Cash Hackathon 2026', 'organizer': 'Fast Prize Team', 'type': 'Hackathon', 'registration_deadline': '2026-12-30', 'mode': 'Online', 'fee': 'Fee required'}),
 'https://medium.com/@x/best-hackathons-2026': ('Top 10 hackathons', 'blog', {'type': 'Other'}),
 'https://web3fest.devfolio.co': ('Web3 Fest 2026', 'Web3 Fest 2026 by ChainClub. Online. Blockchain and Ethereum smart contracts. Registration deadline: 15 December 2026. Registration is free.',
   {'is_single_event': True, 'title': 'Web3 Fest 2026', 'organizer': 'ChainClub', 'type': 'Hackathon', 'registration_deadline': '2026-12-15', 'mode': 'Online', 'fee': 'Free', 'themes': ['Web3']}),
}

def fake_search(query, include, exclude):
    return [{'url': u, 'title': v[0], 'content': v[1][:200], 'raw_content': v[1]} for u, v in PAGES.items()]

def fake_llm(prompt):
    if prompt.startswith("Extract constraints"): return {}
    m = re.search(r'\nURL: (\S+)', prompt)
    return dict(PAGES[m.group(1)][2])

PROFILE = {'skills': ['JavaScript', 'React', 'Python'], 'location': 'Bengaluru, India'}

class UrlTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(D.canonical_url('http://www.Foo.com/a/b/?utm_source=x&ref=y&id=2#frag'), 'https://foo.com/a/b?id=2')
    def test_classify(self):
        k = lambda u: D.classify_url(u)[0]
        self.assertEqual(k('https://devpost.com/hackathons'), 'index'); self.assertEqual(k('https://foo.devpost.com'), 'detail')
        self.assertEqual(k('https://unstop.com/hackathons'), 'index'); self.assertEqual(k('https://unstop.com/hackathons/foo-1'), 'detail')
        self.assertEqual(k('https://devfolio.co/hackathons'), 'index'); self.assertEqual(k('https://x.devfolio.co'), 'detail')
        self.assertEqual(k('https://hackathon.com/city/bangalore'), 'index'); self.assertEqual(k('https://myhack.org/'), 'other')
        self.assertEqual(k('https://myhack.org/hackathons'), 'index')

class DateTests(unittest.TestCase):
    def test_parse(self):
        for s in ['2026-12-20', '20 Dec 2026', '20th December 2026', 'Dec 20, 2026', '20/12/2026', 'December 20th, 2026']:
            self.assertEqual(D.parse_date(s), datetime.date(2026, 12, 20), s)
        self.assertIsNone(D.parse_date('sometime soon'))
    def test_locate(self):
        self.assertTrue(D.locate_date(datetime.date(2026, 12, 20), 'Closes on 20th Dec, 2026 at noon'))
        self.assertTrue(D.locate_date(datetime.date(2026, 12, 20), 'Deadline Dec 20 (2026 edition)'))
        self.assertEqual(D.locate_date(datetime.date(2026, 12, 21), 'Closes on 20th Dec, 2026'), '')
    def test_text_deadline(self):
        d, kind, _ = D.find_deadline_in_text('Registration opens 1 Nov 2026. Registrations close on 15 December 2026.')
        self.assertEqual((d, kind), (datetime.date(2026, 12, 15), 'registration'))
    def test_hallucinated_date_is_unverified(self):
        dl = D.resolve_deadline({'registration_deadline': '2026-12-31'}, 'Applications open soon in Pune.', TODAY)
        self.assertFalse(dl['verified'])
        st, _ = D.resolve_status({}, dl, 'Applications open soon', None, None, TODAY)
        self.assertEqual(st, 'Unknown')               # never "Open" from an unverified date
    def test_ai_date_replaced_by_page_date(self):
        dl = D.resolve_deadline({'registration_deadline': '2026-12-31'}, 'Registration deadline: 15 December 2026', TODAY)
        self.assertEqual(dl['date'], datetime.date(2026, 12, 15)); self.assertTrue(dl['verified'])
    def test_status(self):
        past = D.resolve_deadline({'registration_deadline': '2026-10-01'}, 'Registration deadline: 1 October 2026', TODAY)
        self.assertEqual(D.resolve_status({}, past, '', None, None, TODAY)[0], 'Closed')
        fut = D.resolve_deadline({'registration_deadline': '2026-12-20'}, 'Registration deadline: 20 December 2026', TODAY)
        self.assertEqual(D.resolve_status({}, fut, '', None, None, TODAY)[0], 'Open')
        nodl = D.resolve_deadline({}, 'Registrations are closed.', TODAY)
        self.assertEqual(D.resolve_status({}, nodl, 'Registrations are closed.', None, None, TODAY)[0], 'Closed')

class FeeTests(unittest.TestCase):
    def test_free_needs_evidence(self):
        self.assertEqual(D.resolve_fee({'fee': 'Free'}, 'Win free swag and free food!')[0], 'Unknown')
        self.assertEqual(D.resolve_fee({'fee': 'Free'}, 'There is no registration fee.')[0], 'Free')
    def test_amount_must_be_on_page(self):
        self.assertEqual(D.resolve_fee({'fee': 'Fee required', 'registration_fee': '₹999', 'fee_evidence': 'Fee is ₹999'}, 'Registration fee: ₹500')[1], '₹500')

class DedupeTests(unittest.TestCase):
    def test_same_event(self):
        self.assertTrue(D.same_event('HackXYZ 2026 | Devpost', 'HackXYZ 2026 - Unstop'))
        self.assertFalse(D.same_event('HackXYZ 2025', 'HackXYZ 2026'))
        self.assertFalse(D.same_event('Web3 Fest 2026', 'AI for Good Hackathon 2026'))

class RequirementTests(unittest.TestCase):
    def test_parse(self):
        r = D.parse_requirements('free beginner friendly online AI hackathon in Bengaluru with prizes next month', today=TODAY)
        self.assertIn('AI/ML', r['themes']); self.assertEqual(r['location'], 'bengaluru'); self.assertEqual(r['mode'], 'Online')
        self.assertTrue(r['freeOnly'] and r['beginner'] and r['prizes']); self.assertEqual(r['window'][0], datetime.date(2026, 12, 1))
    def test_filters_override(self):
        r = D.parse_requirements('hackathons', city='Pune', fee='Free', mode='In-person', today=TODAY)
        self.assertEqual((r['location'], r['mode'], r['freeOnly'], r['hardFee'], r['hardMode']), ('Pune', 'In-person', True, True, True))
    def test_queries_bounded(self):
        r = D.parse_requirements('AI hackathon in India', today=TODAY); qs = D.build_queries(r, TODAY)
        self.assertLessEqual(len(qs), 4); self.assertTrue(all('2026' in q for _, q, _ in qs)); self.assertTrue(any(d is None for _, _, d in qs))

class TrustTests(unittest.TestCase):
    def _item(self, **kw):
        base = {'source': 'https://x.devpost.com', 'org': 'GreenTech Labs', 'officialUrl': '', 'fee': 'Free', 'deadline': '2026-12-20', 'deadlineVerified': True, 'feeEvidence': ''}; base.update(kw); return base
    def test_upi_flagged_with_evidence(self):
        t = D.trust_assess(self._item(org='Fast Prize'), 'Fast Prize hackathon. Pay Rs 999 to scam123@ybl now', [])
        self.assertTrue(t['highRisk']); self.assertTrue(any('scam123@ybl' in s['evidence'] for s in t['signals'] if s['kind'] == 'risk'))
    def test_platform_login_otp_not_flagged(self):
        t = D.trust_assess(self._item(), 'GreenTech Labs. Login with OTP sent to your phone.', [])
        self.assertFalse(t['highRisk'])
    def test_user_content_host_is_not_brand(self):
        self.assertEqual(D._brand_owner('sites.google.com'), ''); self.assertEqual(D._brand_owner('events.mlh.io'), 'Major League Hacking')
    def test_levels(self):
        weak = D.trust_assess(self._item(source='https://random.site/x'), 'nothing here', [])
        self.assertEqual(weak['level'], 'none')
        mod = D.trust_assess(self._item(), 'Organized by GreenTech Labs', [])
        self.assertEqual(mod['level'], 'moderate')
        strong = D.trust_assess(self._item(), 'Organized by GreenTech Labs', ['greentechlabs.org'])
        self.assertEqual(strong['level'], 'strong')

class PipelineTests(unittest.TestCase):
    def run_q(self, q, **kw):
        return D.discover(q, profile=PROFILE, search_fn=fake_search, llm_fn=fake_llm, today=TODAY, **kw)
    def test_end_to_end(self):
        out = self.run_q('free online AI hackathon for beginners'); items = out['items']; d = out['diagnostics']
        titles = [i['title'] for i in items]
        self.assertNotIn('Expired Hack 2026', titles)                      # expired
        self.assertNotIn('OldHack 2023', titles)                           # stale edition
        self.assertFalse(any('Top 10' in t for t in titles))               # blog
        self.assertEqual(sum('AI for Good' in t for t in titles), 1)       # deduped across Devpost + Unstop
        top = items[0]
        self.assertEqual(top['title'], 'AI for Good Hackathon 2026')       # best match for the request
        self.assertEqual(top['status'], 'Open'); self.assertTrue(top['deadlineVerified']); self.assertEqual(top['deadline'], '2026-12-20')
        self.assertEqual(len(top['alsoListedOn']), 1); self.assertEqual(top['fee'], 'Free')
        self.assertTrue(top['matchReasons']); self.assertGreater(top['relevance'], 60)
        self.assertEqual(d['duplicatesMerged'], 1); self.assertGreaterEqual(d['dropped']['listingPage'], 3); self.assertGreaterEqual(d['dropped']['expired'], 1)
        self.assertGreaterEqual(d['dropped']['staleEdition'], 1)
        self.assertEqual(top['source'].split('?')[0].rstrip('/').count('?'), 0)
    def test_unverified_date_never_open(self):
        items = self.run_q('hackathon in Pune')['items']; h = [i for i in items if i['title'] == 'Halluc Hack 2026']
        self.assertTrue(h); self.assertEqual(h[0]['status'], 'Unknown'); self.assertFalse(h[0]['deadlineVerified'])
    def test_scam_is_flagged_and_ranked_low(self):
        items = self.run_q('online hackathon')['items']; s = [i for i in items if 'Mega Cash' in i['title']]
        if s:
            self.assertTrue(s[0]['verification']['highRisk']); self.assertFalse(s[0]['organizerVerified'])
            self.assertLess(items.index(s[0]), len(items))
            self.assertGreater(items[0]['relevance'], s[0]['relevance'])
    def test_city_and_fee_requirements(self):
        items = self.run_q('web hackathon', city='Bengaluru')['items']
        self.assertEqual(items[0]['title'], 'BLR Build Hack 2026')
        self.assertEqual(items[0]['registrationFee'], 'Rs. 500')
        free = self.run_q('hackathon', fee='Free')['items']
        self.assertFalse(any(i['fee'] == 'Fee required' for i in free))     # hard filter on a verified paid event
    def test_theme_ranking(self):
        items = self.run_q('web3 blockchain hackathon')['items']
        self.assertEqual(items[0]['title'], 'Web3 Fest 2026')
    def test_mode_hard_filter(self):
        items = self.run_q('hackathon', mode='In-person')['items']
        self.assertFalse(any(i['mode'] == 'Online' for i in items))
    def test_no_llm_fallback_still_verifies(self):
        out = D.discover('AI hackathon', profile=PROFILE, search_fn=fake_search, llm_fn=None, today=TODAY)
        for i in out['items']:
            self.assertIn('Pattern extraction', i['extractionMethod'])
            if i['deadline']: self.assertTrue(i['deadlineVerified'])
    def test_all_searches_fail(self):
        def bad(q, a, b): raise RuntimeError('boom')
        with self.assertRaises(RuntimeError): D.discover('x hackathon', search_fn=bad, llm_fn=None, today=TODAY)

if __name__ == '__main__': unittest.main(verbosity=2)
