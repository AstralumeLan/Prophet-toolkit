"""Public source regressions: Renhuai123/ziwei-doushu commit 495b79e (MIT)."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _cli(*args):
    p = subprocess.run([str(ROOT/'bin/prophet'),'ziwei',*args],cwd=ROOT,text=True,capture_output=True,timeout=15)
    r = json.loads(p.stdout)
    assert p.returncode == 0, r
    return r


def _chart(date,time,**options):
    extra=[v for k,val in options.items() for v in ('--'+k.replace('_','-'),str(val))]
    return _cli('chart','--date',date,'--time',time,'--place','北京','--gender','male',*extra)


def test_ziwei_s01_cli_comparison_and_annual():
    r=_cli('compare','--person','S01','--year','2026')
    assert r['agree'] and r['diffs']==[]
    assert len(r['iztro']['palaces'])==12 and len(r['daxian'])==12
    assert len(r['sihua'])==4
    assert r['annual']['year']==2026 and len(r['annual']['mutagen'])==4
    # Fictional S01 computed once; annual calendar and four transformations checked above.
    assert r['annual']['mingPalace']=='午'
    assert r['input']['time']=='08:45'


def test_ziwei_pan_integrity():
    # scripts/regression/pan-integrity.test.ts: 12 branches/palaces and 紫府 symmetry.
    for date,time in [('1960-01-05','00:30'),('1995-07-15','12:00'),('2010-10-25','18:00')]:
        c=_chart(date,time)['renhuai']
        assert len(c['palaces'])==12
        assert sorted(p['branch'] for p in c['palaces'])==list(range(12))
        pos={s['name']:p['branch'] for p in c['palaces'] for s in p['stars'] if s['type']=='major'}
        assert len(pos)==14 and (pos['紫微']+pos['天府'])%12==4
        for p in c['palaces']:
            names={s['name'] for s in p['stars']}
            if {'天机','天梁'} <= names:
                assert p['branch'] in (4,10)


def test_ziwei_lichun_reference():
    # scripts/regression/sizhu-lichun-boundary.test.ts, 2004 Li Chun 19:56.
    c=_chart('2004-02-04','02:40')['renhuai']['lunarInfo']
    assert c['fourPillars']==['癸未','乙丑','癸丑','癸丑']
    assert c['fourPillarsLunar'][0]=='甲申'
    assert _chart('2004-02-04','22:00')['renhuai']['lunarInfo']['fourPillars'][0]=='甲申'


def test_ziwei_time_index_reference():
    # scripts/regression/iztro-time-index-boundary.test.ts: late zi advances date.
    early=_chart('2000-01-31','00:30')
    late=_chart('2000-01-31','23:30')
    nxt=_chart('2000-02-01','00:30')
    assert early['timeIndex']==0 and late['timeIndex']==12
    assert late['renhuai']['birthInfo']['day']==1
    assert late['renhuai']['birthInfo']['month']==2
    assert early['renhuai']['birthInfo']['day']==31
    assert late['comparison']['agree']
    assert late['renhuai']['palaces']==nxt['renhuai']['palaces']


def test_ziwei_famous_reference():
    # lib/ziwei/famous.ts ma-yun: 1964-09-10, branch index 5 (巳), male.
    # Original repo has no node_modules. Expected computed once with the unmodified
    # copied generateChart: mingGongBranch=4 (辰), major stars=[贪狼].
    # This locks the source fixture, not a verified historical birth time.
    c=_chart('1964-09-10','10:00')['renhuai']
    assert c['mingGongBranch']==4
    p=next(p for p in c['palaces'] if p['name']=='命宫')
    assert [s['name'] for s in p['stars'] if s['type']=='major']==['贪狼']


def test_ziwei_approx_and_true_solar():
    for person in ('S02','S04'):
        r=_cli('chart','--person',person)
        assert r['branches'] and 'invariants' in r
        assert r['input']['time'] is None
        assert len(r['invariants']['不随时间变化']['生年四化星'])==4
    r=_cli('chart','--person','S01','--time-standard','true-solar','--school','ZZ','--leap-month','prev-month')
    assert r['input']['time']=='08:45'
    assert r['candidate']['solar_time']['真太阳时'].startswith('1990-03-15 08:21')
    # A range crossing midnight must keep early/late zi as distinct candidates.
    r=_cli('chart','--date','2000-01-31','--time-range','23:30-00:30','--place','北京','--gender','male')
    assert [b['timeIndex'] for b in r['branches']]==[12,0]
