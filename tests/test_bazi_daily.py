"""Offline references: 6tail lunar-python calendar / LunarTime APIs."""
import json
import subprocess
from lunar_python import Solar
from cli import build_parser
from eastern.bazi import daily, run_daily


def query(*args):
    parser, _ = build_parser()
    return run_daily(parser.parse_args(['bazi', 'daily', *args]))


def test_bazi_daily_reference_dates():
    # 6tail calendar (https://6tail.cn/calendar/), lunar-python Solar/EightChar API.
    c = daily('2020-01-01')
    assert [c['pillars'][k]['ganzhi'] for k in ('year', 'month', 'day')] == ['己亥', '丙子', '癸卯']
    c = daily('2026-10-31')
    assert c['liuri']['ganzhi'] == '戊寅'
    assert c['liuri']['nayin'] == '城头土'
    assert c['day_tianshen'] == {'name': '司命', 'type': '黄道', 'luck': '吉'}
    assert c['liuri']['ganzhi'] == Solar.fromYmdHms(2026,10,31,12,0,0).getLunar().getEightChar().getDay()


def test_bazi_daily_tianshen_rule_table():
    # 十二时神通行表: 寅申日子起青龙，卯酉日寅起青龙。
    # 6tail lunar-python LunarTime.getTianShen/getTianShenType/getTianShenLuck.
    names = ['青龙','明堂','天刑','朱雀','金匮','天德','白虎','玉堂','天牢','玄武','司命','勾陈']
    yellow = {'青龙','明堂','金匮','天德','玉堂','司命'}
    for date, start in [('2026-10-31',0), ('2020-01-01',2)]:
        c = daily(date)
        assert ''.join(h['branch'] for h in c['hours']) == '子丑寅卯辰巳午未申酉戌亥'
        for i, hour in enumerate(c['hours']):
            seg = hour['segments'][0]
            assert seg['tianshen'] == names[(i-start)%12]
            assert (seg['tianshen_type'] == '黄道') == (seg['tianshen'] in yellow)
            h = 0 if i == 0 else 2*i-1
            t = Solar.fromYmdHms(*map(int,date.split('-')),h,30,0).getLunar().getTime()
            assert (seg['tianshen'],seg['tianshen_type'],seg['tianshen_luck']) == (t.getTianShen(),t.getTianShenType(),t.getTianShenLuck())


def test_bazi_daily_zi_sect_and_boundaries():
    a = daily('2026-10-31', sect=1); b = daily('2026-10-31', sect=2)
    assert len(a['hours']) == 12
    early, late = a['hours'][0]['segments']
    assert early['time_range'] == '00:00-01:00' and late['time_range'] == '23:00-24:00'
    assert late['day_ganzhi'] != b['hours'][0]['segments'][1]['day_ganzhi']
    assert late['ganzhi'] == b['hours'][0]['segments'][1]['ganzhi']
    assert daily('2020-02-04')['liunian']['ganzhi'] == '己亥'  # 立春17:03, noon still before it.
    assert daily('2020-02-04', year_boundary='spring-festival')['liunian']['ganzhi'] == '庚子'
    assert daily('2020-02-04', tz='America/New_York')['liunian']['ganzhi'] == '庚子'


def test_bazi_daily_person_and_approx():
    # Fictional S01: 己土日主；丙火为正印，甲木为正官 (五行生克).
    c = query('--date','2026-10-31','--person','S01')
    assert c['day_master'] == '己'
    assert c['liunian']['stem_ten_god'] == '正印'
    assert c['hours'][0]['segments'][1]['stem_ten_god'] == '正官'  # 甲子
    assert c['active_dayun']['ganzhi']
    assert c['input']['date'] == '1990-03-15'
    for p in c['pillars'].values():
        assert len(p['hidden_stems']) == len(p['hidden_ten_gods'])
    approx = query('--date','2026-10-31','--person','S02','--time-standard','clock')
    assert len(approx['birth_candidates']) == 2 and 'candidates' not in approx
    varying = query('--date','2026-10-31','--birth-date','2005-12-23', '--time-range','23:30-00:30','--place','北京','--time-standard','clock')
    assert len(varying['candidates']) == 2
    assert 'day_master' in varying['invariants']['随时间变化']
    assert query('--date','1980-01-01','--person','S01')['active_dayun'] is None


def test_bazi_daily_cli_and_legacy_rules():
    c = json.loads(subprocess.check_output(['bin/prophet','bazi','daily','--date','2026-10-31'],text=True))
    assert c['liuri']['ganzhi'] == '戊寅' and c['warnings'] == []
    from tests.test_bazi import invoke
    from pathlib import Path
    from tests.schema import check_schema
    check_schema(invoke('chart','--person','S01'), 'bazi')
