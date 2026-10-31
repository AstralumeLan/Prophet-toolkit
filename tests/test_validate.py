"""Public reference: https://github.com/SylarLong/iztro README,
astro.bySolar('2000-8-16', 2, '女', true, 'zh-CN').
Classical reference: 紫微斗数全书 安紫微星诀（补日整除、偶进奇退）.
"""
import contextlib
import io
import json
import random
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache
from cli import main
from eastern.ziwei import JS
from validate.cross import ziwei_check
from validate.ziwei_indep import calculate


@lru_cache(None)
def cli(*argv):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = main(list(argv))
    data = json.loads(stream.getvalue())  # Also verifies exactly one JSON document.
    assert code == 0, data
    return data


def test_validate_all_s01_and_readme():
    r = cli('validate','all','--person','S01')
    assert all(x['agree'] for x in r['summary'].values()), r['summary']
    r = cli('validate','all','--date','2000-08-16','--time','03:00','--gender','女','--place','北京')
    assert all(x['agree'] for x in r['summary'].values()), r['summary']
    c = r['results']['ziwei']['independent']['chart']
    # Frozen public README example: 寅时、六月十七，命午木三局，紫微午、天府戌.
    assert (c['soul'],c['body'],c['bureau']) == ('午','戌','木三局')
    assert c['positions']['紫微']=='午' and c['positions']['天府']=='戌'


def test_validate_ziwei_seeded_40_and_boundaries():
    rng = random.Random(20261031)
    start = datetime(1950,1,1)
    dates = [start+timedelta(days=rng.randrange((datetime(2031,1,1)-start).days),hours=rng.randrange(24)) for _ in range(40)]
    # Explicit leap-month halves, late 子, lunar/year/month transitions.
    dates += [datetime.fromisoformat(x) for x in (
        '2023-03-25T03:00','2023-04-10T03:00','2023-04-10T23:00',
        '2023-04-19T23:00','2024-02-09T23:00','2000-08-16T03:00')]
    requests = [dict(date=d.strftime('%Y-%m-%d'),hour=d.hour,minute=d.minute,gender='female',year=None,school='default',leapMonth='split') for d in dates]
    # Existing ziwei Node bridge accepts a batch; no shell invocation or new engine.
    proc = subprocess.run(['node','--import','tsx',str(JS/'cli.ts')],cwd=JS,
                          input=json.dumps({'candidates':requests}),text=True,capture_output=True,timeout=15)
    assert proc.returncode==0, proc.stderr
    rows = json.loads(proc.stdout)['results']
    assert len(rows)==len(dates)
    for dt,row in zip(dates,rows):
        check = ziwei_check(dt,row)
        assert check['independent']['agree'], (str(dt),check['diff'])
        assert len([s for s in calculate(dt)['positions'] if s not in ('文昌','文曲','左辅','右弼')])==14


def test_validate_approx_cli_and_midnight():
    for person in ('S02','S04'):
        r = cli('validate','all','--person',person)
        assert r['invariants']
        for name,item in r['results'].items():
            assert item['branches'] and item['invariants'], name
    r = cli('validate','ziwei','--date','2023-04-19','--time-range','23:00-00:15','--place','北京','--gender','女')
    assert len(r['branches'])>=2
    assert len({b['candidate']['dt'][:10] for b in r['branches']})==2


def test_validate_bazi_rule_difference_visible():
    r = cli('validate','bazi','--date','2024-02-05','--time','12:00','--place','北京','--gender','女')
    assert not r['agree']
    year = next(d for d in r['diff'] if d['field']=='year')
    assert year['engine_a']=='甲辰' and year['engine_b']=='癸卯'
    assert 'year' in r['rule_notes'][0]


def test_validate_independent_mismatch_is_concrete():
    from copy import deepcopy
    from eastern.ziwei import run
    from argparse import Namespace
    dt=datetime(2000,8,16,3)
    raw=run(Namespace(date='2000-08-16',time='03:00',place='北京',gender='女',
                      time_standard='clock',year=None,school='default',leap_month='split',save_cache=False,sub='chart'))
    wrong=deepcopy(raw)
    for p in wrong['iztro']['palaces']:
        for s in p['majorStars']:
            if s['name']=='紫微':
                p['earthlyBranch']='子'
    r=ziwei_check(dt,wrong)
    assert not r['agree']
    assert difference_present(r['diff'],'positions.紫微','子','午')


def difference_present(rows,field,a,b):
    return any(d['field']==field and d['engine_a']==a and d['engine_b']==b for d in rows)
