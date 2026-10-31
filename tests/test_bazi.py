"""Regression sources: 6tail/lunar-python README EightChar example and JieQi API."""
import json
import subprocess
from datetime import datetime, timedelta
from lunar_python import Solar
from cli import build_parser
from eastern.bazi import run


def invoke(*args):
    parser, _ = build_parser()
    return run(parser.parse_args(['bazi', *args]))


def example(time='08:37', *extra):
    return invoke('chart', '--date', '2005-12-23', '--time', time,
                  '--place', '北京', '--gender', 'male', '--time-standard', 'clock', *extra)['candidates'][0]


def test_bazi_documented_example():
    # https://github.com/6tail/lunar-python : EightChar 2005-12-23 08:37.
    c = example()
    assert [c[k+'_pillar'] for k in ('year','month','day','hour')] == ['乙酉','戊子','辛巳','壬辰']
    assert c['day_master']=='辛'
    assert len(c['dayun']['steps']) == 10
    assert sum(c['five_elements'].values()) == 8
    assert c['pillars']['hour']['stem_ten_god']=='伤官'
    assert c['pillars']['day']['hidden_stems']==['丙','庚','戊']


def test_bazi_lichun_exact_boundary():
    # Public lunar-python JieQi API: 2020 立春 2020-02-04 17:03:12 Beijing.
    t=Solar.fromYmdHms(2020, 6, 1, 0, 0, 0).getLunar().getJieQiTable()['立春']
    dt=datetime.strptime(t.toYmdHms(), '%Y-%m-%d %H:%M:%S')
    assert dt.strftime('%Y-%m-%d %H:%M')=='2020-02-04 17:03'
    charts=[]
    for when in (dt-timedelta(minutes=1), dt+timedelta(minutes=1)):
        c=invoke('chart','--date',str(when.date()),'--time',when.strftime('%H:%M'),
                 '--place','北京','--time-standard','clock')['candidates'][0]
        charts.append(c)
        assert c['nearby_solar_terms'][0]['exact_time']==t.toYmdHms()
    assert [c['year_pillar'] for c in charts]==['己亥','庚子']
    c=invoke('chart','--date','2020-02-01','--time','12:00','--place','北京',
             '--year-boundary','spring-festival')['candidates'][0]
    assert c['year_pillar']=='庚子'


def test_bazi_zi_sect():
    a=example('23:30','--sect','1'); b=example('23:30','--sect','2')
    assert a['day_pillar'] != b['day_pillar']
    assert a['warnings'] and b['warnings']


def test_bazi_s01_and_cli():
    result=subprocess.run(['bin/prophet','bazi','chart','--person','S01'],capture_output=True,text=True,check=True)
    out=json.loads(result.stdout); c=out['candidates'][0]
    e=Solar.fromYmdHms(1990,3,15,8,45,0).getLunar().getEightChar()
    assert [c[k+'_pillar'] for k in ('year','month','day')]==[e.getYear(),e.getMonth(),e.getDay()]
    # Fictional S01 values computed once; checked against lunar-python calendar.
    assert c['year_pillar']=='庚午' and c['month_pillar']=='己卯'
    assert c['clock_hour_pillar'][-1]==c['true_solar_hour_pillar'][-1]=='辰'
    assert not c['hour_pillars_differ']
    assert out['input']['time']=='08:45' and out['engine']['rules']['sect']==2


def test_bazi_s02_branches():
    out=invoke('chart','--person','S02','--time-standard','clock')
    assert len(out['candidates'])==2
    assert out['input']['time'] is None
    assert out['input']['time_range']==['20:00','21:00']
    stable=out['invariants']['不随时间变化']
    assert 'day_master' in stable and 'day_pillar' in stable
    assert 'hour_pillar' in out['invariants']['随时间变化']


def test_bazi_forecasts_cli():
    for command in ('liunian','liuyue'):
        p=subprocess.run(['bin/prophet','bazi',command,'--person','S01','--year','2026'],capture_output=True,text=True,check=True)
        out=json.loads(p.stdout); c=out['candidates'][0]
        assert out['engine']['rules']['forecast_year']==2026
        if command=='liunian':
            assert c['liunian']['ganzhi']=='丙午'
            assert c['liunian']['dayun'] is not None
        else:
            assert len(c['liuyue'])==12
            assert c['liuyue'][0]['ganzhi']=='庚'+'寅'
            assert c['liuyue'][-1]['start'].startswith('2027-01')


def test_bazi_approx_internal_boundaries():
    out=invoke('chart','--date','2020-02-04','--time-range','17:00-17:10',
               '--place','北京','--time-standard','clock')
    assert {c['year_pillar'] for c in out['candidates']}=={'己亥','庚子'}
    assert 'year_pillar' in out['invariants']['随时间变化']
    out=invoke('chart','--date','2005-12-23','--time-range','23:30-00:30',
               '--place','北京','--time-standard','clock','--sect','2')
    assert len({c['day_pillar'] for c in out['candidates']})==2


def test_bazi_cache_and_correction():
    import tempfile
    from pathlib import Path
    import core.cache as cache
    old=cache.CACHE
    try:
        with tempfile.TemporaryDirectory(prefix='prophet-bazi-') as tmp:
            cache.CACHE=Path(tmp)
            out=invoke('chart','--person','S01','--save-cache')
            saved=json.loads(Path(out['cache_path']).read_text())
            assert saved['person']=='S01'
            assert saved['engine']==out['engine']
    finally:
        cache.CACHE=old
    c=invoke('chart','--date','2001-09-20','--time','09:00','--place','广州','--time-standard','clock')['candidates'][0]
    assert c['clock_hour_pillar'][-1]=='巳'
    assert c['true_solar_hour_pillar'][-1]=='辰'
    assert c['hour_pillars_differ'] and c['warnings']
