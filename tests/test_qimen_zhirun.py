"""Published 置闰 examples: 周新春易学网置闰 article (1898, not 1998),
《奇门遁甲统宗·置闰法》 and 张志春《神奇之门》.
References are transcribed from the supervisor's source corrections; no network.
"""
import json
import subprocess
from datetime import datetime, timedelta
from lunar_python import Solar
from eastern.qimen import chart, ENGINE
from eastern._qimen_zhirun import context, timeline, term_instants
from eastern._cf.qimen_tables import YANG_JIE_QI, YIN_JIE_QI


def at(day):
    return datetime.fromisoformat(day + 'T12:00:00+08:00')


def day_ganzhi(day):
    d = at(day)
    return Solar.fromYmd(d.year, d.month, d.day).getLunar().getDayInGanZhi()


def check(day, ganzhi, term, dun, ju, threshold=9):
    assert day_ganzhi(day) == ganzhi
    r = chart(at(day), ju_method='zhirun', zhirun_threshold=threshold)
    assert (r['jieqi_used'], r['san_yuan'], r['ju_type'], r['ju_number']) == (term, '上元', dun, ju)
    assert r['ganzhi']['day'] == ganzhi and len(r['palaces']) == 9
    return r


def test_qimen_zhirun_published_1901_1959_2024():
    # Published examples supplied in task, classical sources named above.
    for day, gz, term, dun, ju in [
        ('1901-11-27', '己酉', '大雪', '阴遁', 4),
        ('1901-12-12', '甲子', '闰大雪', '阴遁', 4),
        ('1901-12-27', '己卯', '冬至', '阳遁', 1),
        ('1959-05-27', '己酉', '芒种', '阳遁', 6),
        ('1959-06-11', '甲子', '闰芒种', '阳遁', 6),
        ('1959-06-26', '己卯', '夏至', '阴遁', 9),
        ('2024-12-11', '己酉', '闰大雪', '阴遁', 4),
        ('2024-12-26', '甲子', '冬至', '阳遁', 1),
    ]:
        check(day, gz, term, dun, ju)
    r = check('1901-11-27', '己酉', '大雪', '阴遁', 4)
    assert (r['zhirun_context']['status'], r['zhirun_context']['day_count']) == ('超神', 11)
    r = check('2024-12-26', '甲子', '冬至', '阳遁', 1)
    assert (r['zhirun_context']['status'], r['zhirun_context']['day_count']) == ('接气', 5)


def test_qimen_zhirun_1996_default_solstice_lead():
    # Published 1996 example: 夏至 June 21 minus would-be June 11 = 10 days.
    check('1996-06-11', '己卯', '闰芒种', '阳遁', 6)
    check('1996-06-26', '甲午', '夏至', '阴遁', 9)
    r = context(at('1996-05-27'))
    assert r['signed_lead_days'] == 9 and r['base_jieqi'] == '芒种'
    assert r['term_offset_days'] == 9 and r['solstice_lead_days'] == 10
    assert context(at('1996-06-11'))['is_leap']


def test_qimen_zhirun_1898_published_reference():
    # 周新春易学网置闰 article: 公历1898; all six dates from the source.
    for day, gz, term, yuan, ju in [
        ('1898-11-27', '甲午', '大雪', '上元', 4),
        ('1898-12-02', '己亥', '大雪', '中元', 7),
        ('1898-12-07', '甲辰', '大雪', '下元', 1),
        ('1898-12-12', '己酉', '闰大雪', '上元', 4),
        ('1898-12-22', '己未', '闰大雪', '下元', 1),
        ('1898-12-27', '甲子', '冬至', '上元', 1),
    ]:
        r = chart(at(day), ju_method='zhirun')
        assert r['ganzhi']['day'] == day_ganzhi(day) == gz
        assert (r['jieqi_used'], r['san_yuan'], r['ju_number']) == (term, yuan, ju)
        assert r['ju_type'] == ('阳遁' if term == '冬至' else '阴遁')


def test_qimen_zhirun_1995_school_threshold():
    # 刘金喜/郭志诚/张志春: no leap; 刘广斌《奇门预测学》: leap.
    # 《奇门遁甲统宗·置闰法》康熙五十七年例 uses 8 days (9 inclusive).
    normal = check('1995-12-14', '己卯', '冬至', '阳遁', 1)
    leap = check('1995-12-14', '己卯', '闰大雪', '阴遁', 4, 7)
    assert normal['zhirun_context']['solstice_lead_days'] == 8
    assert leap['zhirun_context']['solstice_lead_days'] == 8
    assert normal['zhirun_context']['term_instant'].startswith('1995-12-22')
    assert (normal['zhirun_context']['status'], normal['zhirun_context']['day_count']) == ('超神', 8)
    assert leap['zhirun_context']['term_offset_days'] == -7
    assert (leap['zhirun_context']['status'], leap['zhirun_context']['day_count']) == ('接气', 7)
    assert not context(at('1995-12-14'), 8)['is_leap']


def test_qimen_zhirun_standard_table():
    # Standard 二十四节气三元用局表, 《奇门遁甲统宗》, supplied task transcription.
    assert list(YANG_JIE_QI.values()) == [(1,7,4),(2,8,5),(3,9,6),(8,5,2),
        (9,6,3),(1,7,4),(3,9,6),(4,1,7),(5,2,8),(4,1,7),(5,2,8),(6,3,9)]
    assert list(YIN_JIE_QI.values()) == [(9,3,6),(8,2,5),(7,1,4),(2,5,8),
        (1,4,7),(9,3,6),(7,1,4),(6,9,3),(5,8,2),(6,9,3),(5,8,2),(4,7,1)]


def test_qimen_zhirun_continuity_and_yuan_boundaries():
    rows = timeline()
    for previous, current in zip(rows, rows[1:]):
        assert (current[0] - previous[0]).days == 15
        if current[2]:
            assert current[1] in ('芒种', '大雪') and not previous[2]
            assert current[1] == previous[1] and current[4] > 9
    for day in ['1900-01-01', '2100-12-31']:
        r = chart(at(day), ju_method='zhirun')
        head = r['zhirun_context']['upper_yuan_start']
        assert day_ganzhi(head) in ('甲子', '甲午', '己卯', '己酉')
    start = at('2024-12-11').replace(hour=0)
    assert context(start - timedelta(seconds=1))['san_yuan'] == '下元'
    assert context(start)['jieqi_used'] == '闰大雪'
    assert context(start + timedelta(days=5))['san_yuan'] == '中元'
    assert context(start + timedelta(days=10))['san_yuan'] == '下元'
    assert context(start + timedelta(days=15))['jieqi_used'] == '冬至'


def test_qimen_zhirun_zhengshou_and_default_compatibility():
    # 正授: term civil date == upper-yuan 符头, so both methods use same 局.
    found = False
    for instant, name in term_instants(1959):
        dt = instant + timedelta(minutes=1)
        z = chart(dt, ju_method='zhirun')
        if z['zhirun_context']['status'] == '正授' and z['jieqi_used'] == name:
            c = chart(dt)
            assert z['ju_number'] == c['ju_number'] and z['palaces'] == c['palaces']
            found = True
    assert found
    r = chart(at('2024-12-21').replace(hour=18, minute=14))
    assert r['jieqi'] == '冬至' and r['ju_type'] == '阳遁'
    assert chart(at('2024-12-21'), ju_method='zhirun')['ju_type'] == '阴遁'
    assert r['engine'] == ENGINE
    assert r['engine']['rules'] == {
        'plate': 'rotating-compat', 'ju_method': '拆补：符头三元+实交节',
        'center': '环盘中五寄坤二；天禽保留中五',
        'calendar': 'solar terms at actual UTC+08 instant',
        'day_boundary': 'midnight', 'horse': 'hour branch 三合驿马'}
    for alias in ['拆补', 'futou']:
        assert chart(at('2024-12-21'), ju_method=alias) == chart(at('2024-12-21'))


def test_qimen_zhirun_cli_aliases_ranges_and_errors():
    for alias in ['zhirun', '置闰']:
        p = subprocess.run(['bin/prophet', 'qimen', 'chart', '--datetime', '2024-12-11T12:00',
                            '--ju-method', alias], capture_output=True, text=True)
        r = json.loads(p.stdout)
        assert p.returncode == 0 and r['jieqi_used'] == '闰大雪'
        assert r['rules_ext']['zhirun_threshold'] == 9
    p = subprocess.run(['bin/prophet', 'qimen', 'chart', '--person', 'S02',
                        '--ju-method', 'zhirun'], capture_output=True, text=True)
    r = json.loads(p.stdout)
    assert p.returncode == 0 and len(r['branches']) == 2 and 'invariants' in r
    p = subprocess.run(['bin/prophet', 'qimen', 'chart', '--datetime', '1995-12-14T12:00',
                        '--ju-method', '置闰', '--zhirun-threshold', '7'], capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)['jieqi_used'] == '闰大雪'
    for day, threshold in [('1898-11-26',9), ('2101-01-01',9), ('2024-01-01',-1), ('2024-01-01',15)]:
        try:
            context(at(day), threshold)
        except ValueError:
            pass
        else:
            assert False, (day, threshold)
