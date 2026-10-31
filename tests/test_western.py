import json
import subprocess
from western.astro import chart, positions_swe, positions_alt, delta, FLAGS
import swisseph as swe


def cli(*args):
    p=subprocess.run(['bin/prophet','western',*args],capture_output=True,text=True)
    assert p.returncode==0,p.stdout+p.stderr
    return json.loads(p.stdout)


def test_western_j2000_reference():
    # Swiss Ephemeris J2000 apparent tropical longitude reference (TT JD 2451545).
    sun=swe.calc(2451545,swe.SUN,FLAGS)[0][0]
    moon=swe.calc(2451545,swe.MOON,FLAGS)[0][0]
    assert abs(sun-280.37)<.02
    assert abs(moon-223.32)<.1


def test_western_einstein_reference_houses():
    # Astro-Databank Albert Einstein: 14 March 1879, 11:30 LMT, Ulm.
    j=swe.julday(1879,3,14,11.5-9.99/15)
    for system in ('placidus','whole-sign'):
        c=chart(j,48.4,9.99,system)
        assert c['angles']['ASC']['sign']=='Cancer'
        assert abs(c['angles']['ASC']['degree_in_sign']-11.65)<.1
        assert abs(c['planets']['Sun']['lon']-353.5)<.05
        assert abs(c['planets']['Moon']['lon']-254.5)<.1
        assert sorted(x['house'] for x in c['houses'])==list(range(1,13))
    assert chart(j,48.4,9.99,'whole-sign')['houses'][0]['lon']==90
    assert chart(j,75,0)['engine']['rules']['house_system']=='porphyry'


def test_western_independent_longitudes():
    for j in (2451545.,2455347.,2461000.):
        x,y=positions_swe(j),positions_alt(j)
        assert max(abs(delta(x[n]-y[n]))*60 for n in list(x)[:7])<1


def test_western_solar_return_and_cli():
    r=cli('solar-return','--person','S01','--year','2026')['branches'][0]
    assert abs(delta(r['return_chart']['planets']['Sun']['lon']-r['natal']['planets']['Sun']['lon']))*3600<1
    assert r['return_chart']['utc'].startswith('2026-')
    for command in ('natal','check','transits','progressions','synastry'):
        extra=['--at','2026-10-31'] if command in ('transits','progressions') else ['--other','S03'] if command=='synastry' else []
        assert cli(command,'--person','S01',*extra)['engine']['name']=='western.astro'


def test_western_approx_candidates():
    r=cli('natal','--person','S02')
    assert len(r['branches'])==5 and r['input']['time'] is None
    assert 'Sun sign' in r['invariants']['不随时间变化']
    assert 'houses' in r['invariants']['随时间变化'] or 'ASC sign' in r['invariants']['随时间变化']
