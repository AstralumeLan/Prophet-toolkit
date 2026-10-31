"""Public references and offline CLI regressions for vedic.jyotish."""
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import swisseph as swe
from vedic.jyotish import (calculate_chart, varga, vimshottari, ashtakavarga,
                           nakshatra, dignity, PLANETS, YEARS, YEAR_DAYS)

ROOT = Path(__file__).resolve().parents[1]


def cli(*args):
    p = subprocess.run([str(ROOT/'bin/prophet'), 'vedic', *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=15)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.loads(p.stdout)


def test_vedic_lahiri_j2000():
    # Swiss Ephemeris Lahiri reference: J2000 TT ~23 degrees 51 arcminutes.
    # https://www.astro.com/swisseph/swephprg.htm (swe_get_ayanamsa)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    assert abs(swe.get_ayanamsa(2451545.0) - 23.85) < .02


def test_vedic_bav_reference_totals_and_profiles():
    # BPHS Ashtakavarga adhyaya: invariant raw totals (48,49,39,54,56,52,39).
    # Dashaflow MIT reference commit f8f8ead76e56b9048f80adbbbff282c007068cf7.
    expected = dict(zip(PLANETS, [48, 49, 39, 54, 56, 52, 39]))
    for shift in range(12):
        signs = {p: (i*3+shift) % 12 for i, p in enumerate(PLANETS)}
        for profile in ('parashara', 'dashaflow'):
            a = ashtakavarga(signs, shift, profile)
            assert a['planet_totals'] == expected
            assert a['grand_total'] == 337
            assert all(0 <= v <= 8 for row in a['BAV'].values() for v in row)
            assert a['SAV'] == [sum(r[i] for r in a['BAV'].values()) for i in range(12)]
    # Specific profile contributions, not merely identical grand totals.
    a = ashtakavarga({p: 0 for p in PLANETS}, 0, 'parashara')
    b = ashtakavarga({p: 0 for p in PLANETS}, 0, 'dashaflow')
    assert a['contributions']['Moon']['Moon'][8] == 1
    assert b['contributions']['Moon']['Moon'][8] == 0
    assert a['contributions']['Venus']['Mars'][3] == 1
    assert b['contributions']['Venus']['Mars'][4] == 1


def test_vedic_varga_public_rules():
    # BPHS Shodashavarga: navamsas start at same/ninth/fifth for movable/fixed/dual.
    assert varga(0, 9) == 0
    assert varga(3.333333-1e-7, 9) == 0
    assert varga(30, 9) == 9
    assert varga(30+3.333333-1e-7, 9) == 9
    assert varga(10/3, 9) == 1
    # Also matches vendor/dashaflow/tests/test_comprehensive.py public fixtures.
    assert varga(5*30+29.46, 9) == 5
    assert varga(6*30+.05, 9) == 6
    assert varga(.5, 7) == 0 and varga(30.5, 7) == 7
    assert varga(5, 10) == 1 and varga(35, 10) == 10
    assert varga(32.5, 12) == 2


def test_vedic_dasha_ashwini_full_ketu_and_continuity():
    # Classical Vimshottari sequence/years; Ashwini is ruled by Ketu, 7 years.
    b = datetime(2000, 1, 1, tzinfo=timezone.utc)
    d = vimshottari(0, b, b, 3)
    assert sum(YEARS.values()) == 120
    assert d['balance_years'] == 7
    assert d['timeline'][0]['lord'] == 'Ketu'
    assert d['timeline'][0]['years'] == 7
    assert all(v['lord'] == 'Ketu' for v in d['current'].values())
    cycle = datetime.fromisoformat(d['cycle_end'])-datetime.fromisoformat(d['cycle_start'])
    assert cycle == timedelta(days=120*YEAR_DAYS)

    def check(period):
        children = period.get('children')
        if children:
            assert children[0]['start'] == period['start']
            assert children[-1]['end'] == period['end']
            for a, c in zip(children, children[1:]):
                assert a['end'] == c['start']
            for c in children:
                check(c)
    for p in d['timeline']:
        check(p)
    boundary = datetime.fromisoformat(d['timeline'][0]['end'])
    assert vimshottari(0, b, boundary)['current']['maha']['lord'] == 'Venus'


def test_vedic_dasha_birth_balance_keeps_original_subperiods():
    b = datetime(2000, 1, 1, tzinfo=timezone.utc)
    d = vimshottari(20/3, b, b, 3)  # halfway through Ashwini/Ketu
    assert abs(d['balance_years']-3.5) < 1e-9
    assert datetime.fromisoformat(d['timeline'][0]['start']) < b
    assert d['current']['maha']['lord'] == 'Ketu'
    assert d['current']['antar']['lord'] != 'Ketu'
    assert 'children' not in vimshottari(0, b, b, 1)['timeline'][0]


def test_vedic_published_dashaflow_delhi_chart():
    # Public MIT dashaflow/tests/test_comprehensive.py Delhi fixture:
    # 1990-04-15 14:30 IST, Delhi 28.6139 N 77.2090 E.
    c = calculate_chart(datetime(1990, 4, 15, 14, 30), 28.6139, 77.2090,
                        'Asia/Kolkata', at='2026-01-01', levels=1)
    assert c['lagna']['sign'] == 'Leo'
    for p, sign in {'Sun': 'Aries', 'Moon': 'Scorpio', 'Saturn': 'Capricorn',
                    'Mars': 'Aquarius', 'Jupiter': 'Gemini'}.items():
        assert c['grahas'][p]['sign'] == sign
    assert c['grahas']['Sun']['dignity'] == 'exalted'
    assert c['grahas']['Moon']['dignity'] == 'debilitated'
    assert c['grahas']['Saturn']['dignity'] == 'own'
    assert c['grahas']['Moon']['house'] == 4


def test_vedic_nakshatra_and_dignity_boundaries():
    assert nakshatra(0)['name'] == 'Ashwini'
    assert nakshatra(0)['lord'] == 'Ketu'
    assert nakshatra(360-1e-7)['name'] == 'Revati'
    assert nakshatra(360-1e-7)['pada'] == 4
    assert nakshatra(10/3)['pada'] == 2
    assert dignity('Sun', 120) == 'moolatrikona'
    assert dignity('Sun', 140) == 'own'
    assert dignity('Sun', 180) == 'debilitated'
    assert dignity('Rahu', 30) == 'unassigned'


def test_vedic_cli_chart_s01_and_true_nodes():
    a = cli('chart', '--person', 'S01', '--at', '2026-10-31')
    assert a['person'] == 'S01' and len(a['branches']) == 1
    c = a['branches'][0]['chart']
    assert c['clock_time'] == '1990-03-15T08:45:00'
    assert c['ashtakavarga']['grand_total'] == 337
    assert set(c['vargas']) == {'D1', 'D7', 'D9', 'D10', 'D12'}
    b = cli('chart', '--person', 'S01', '--node', 'true', '--bav-table', 'dashaflow', '--levels', '1')
    assert b['engine']['rules']['node'] == 'true'
    assert b['branches'][0]['chart']['grahas']['Rahu']['longitude'] != c['grahas']['Rahu']['longitude']


def test_vedic_cli_dasha_nakshatra_approx_branches():
    a = cli('dasha', '--person', 'S02', '--levels', '2', '--at', '2026-10-31')
    assert len(a['branches']) == 5 and a['input']['time'] is None
    assert a['invariants']['不随时间变化']['moon_nakshatra']
    assert a['warnings'] and 'antar' in a['branches'][0]['chart']['dasha']['current']
    b = cli('nakshatra', '--person', 'S02', '--levels', '1')
    assert len(b['branches']) == 5 and 'invariants' in b
    c = cli('chart', '--person', 'S04', '--levels', '1')
    assert len(c['branches']) >= 2 and c['input']['time'] is None
    d = cli('nakshatra', '--date', '2000-01-01', '--time-range', '23:45-00:15', '--place', '北京', '--levels', '1')
    assert len(d['branches']) == 3
    assert d['branches'][-1]['candidate']['dt'].startswith('2000-01-02')


def test_vedic_cache_uses_shared_writer_without_repository_mutation():
    import tempfile
    from unittest.mock import patch
    from cli import build_parser
    # Test the real handler and writer, redirecting all writes to a temporary root.
    with tempfile.TemporaryDirectory() as directory:
        parser, _ = build_parser()
        args = parser.parse_args(['vedic', 'nakshatra', '--person', 'S01',
                                  '--levels', '1', '--at', '2026-10-31', '--save-cache'])
        with patch('core.cache.CACHE', Path(directory)):
            result = args.func(args)
        cached = json.loads(Path(result['cache_path']).read_text())
        assert cached['person'] == 'S01'
        assert cached['engine']['version'] == '1.0.0'
        assert cached['input']['time'] == '08:45'


def test_vedic_round2_node_dignity_conventions():
    # BPHS ch.3 (Santhanam common translation); later Gemini/Sagittarius school.
    for p,ex,deb,mt,own in [('Rahu',1,7,2,10),('Ketu',7,1,8,7)]:
        assert dignity(p,ex*30,'none')=='unassigned'
        assert dignity(p,ex*30,'bphs')=='exalted'
        assert dignity(p,deb*30,'bphs')=='debilitated'
        assert dignity(p,mt*30,'bphs')=='moolatrikona'
        # Ketu own Scorpio overlaps exaltation; exaltation takes precedence.
        assert dignity(p,own*30,'bphs')==('own' if p=='Rahu' else 'exalted')
    for p,ex,deb in [('Rahu',2,8),('Ketu',8,2)]:
        assert dignity(p,ex*30,'gemini-sagittarius')=='exalted'
        assert dignity(p,deb*30,'gemini-sagittarius')=='debilitated'
    c=cli('chart','--person','S01','--levels','1','--node-dignity','bphs')
    assert 'BPHS ch.3' in c['rules_ext']['node_dignity_source']
    assert c['engine']['rules']['node_dignity']=='bphs'


def test_vedic_round2_pvr_exact_rows_and_totals():
    # PVR, Vedic Astrology: An Integrated Approach, Ashtakavarga, Controversies.
    from vedic.jyotish import BAV_PARASHARA, BAV_DASHAFLOW, BAV_PVR, engine
    assert BAV_PVR['Moon']['Moon']==[1,3,6,7,9,10,11]
    assert BAV_PVR['Moon']['Mars']==[2,3,5,6,10,11]
    assert BAV_PVR['Moon']['Jupiter']==[1,2,4,7,8,10,11]
    assert BAV_PVR['Venus']['Mars']==[3,4,6,9,11,12]
    changes=lambda a,b: {(p,q) for p in a for q in a[p] if a[p][q]!=b[p][q]}
    assert changes(BAV_PVR,BAV_PARASHARA)=={('Moon','Jupiter')}
    assert changes(BAV_PVR,BAV_DASHAFLOW)=={('Moon','Moon'),('Moon','Mars'),('Moon','Jupiter'),('Venus','Mars')}
    for profile in ('parashara','dashaflow','varahamihira','pyjhora-pvr'):
        a=ashtakavarga({p:i for i,p in enumerate(PLANETS)},0,profile)
        assert list(a['planet_totals'].values())==[48,49,39,54,56,52,39]
        assert a['grand_total']==337
        if profile=='parashara':
            assert 'Moon/Jupiter' in a['notes'][0]
        if profile=='pyjhora-pvr':
            assert "implemented from PVR's published description; not verified against PyJHora" in a['bav_profile_source']
    a=ashtakavarga({p:0 for p in PLANETS},0,'varahamihira')
    b=ashtakavarga({p:0 for p in PLANETS},0,'dashaflow')
    assert a['BAV']==b['BAV']
    # Default engine rules stay byte-for-byte structurally identical to before.
    assert 'node_dignity' not in engine()['rules']
    assert 'shadbala' not in engine()['rules']
    c=cli('chart','--person','S01','--levels','1','--bav-table','pyjhora-pvr')
    assert 'not verified against PyJHora' in c['branches'][0]['chart']['ashtakavarga']['bav_profile_source']
