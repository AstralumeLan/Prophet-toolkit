"""Offline iztro 2.6.1 horoscope reference and CLI regressions."""
import json
import subprocess
from pathlib import Path
from lunar_python import Solar

ROOT = Path(__file__).resolve().parents[1]


def cli(*args):
    p = subprocess.run([str(ROOT/'bin/prophet'), 'ziwei', *args], cwd=ROOT,
                       text=True, capture_output=True, timeout=30)
    data = json.loads(p.stdout)
    assert p.returncode == 0, data
    return data


def test_ziwei_horoscope_s01_reference_and_locations():
    r = cli('horoscope', '--person', 'S01', '--date', '2026-08-28')
    f = r['flows']
    # Published iztro 2.6.1 lib/data/heavenlyStems.js: 丙 => 同机昌廉.
    # Chinese calendar 2026 丙午; independent lunar-python day calendar below.
    assert f['yearly']['heavenlyStem'] + f['yearly']['earthlyBranch'] == '丙午'
    assert [s['star'] for s in f['yearly']['mutagen']] == ['天同', '天机', '文昌', '廉贞']
    assert [s['transformation'] for s in f['yearly']['mutagen']] == ['化禄', '化权', '化科', '化忌']
    assert f['daily']['heavenlyStem'] + f['daily']['earthlyBranch'] == Solar.fromYmd(2026, 8, 28).getLunar().getDayInGanZhi()
    assert 'hourly' not in f
    assert r['input']['date'] == '1990-03-15' and r['input']['time'] == '08:45'
    age = f['age']['nominalAge']
    assert f['decadal']['age_range'][0] <= age <= f['decadal']['age_range'][1]
    natal = cli('chart', '--person', 'S01')['iztro']['palaces']
    positions = {s['name']: (p['name'], p['earthlyBranch']) for p in natal
                 for kind in ('majorStars', 'minorStars', 'adjectiveStars') for s in p[kind]}
    for flow in f.values():
        assert len(flow['palace_names']) == 12
        assert flow['palace_names']['命宫'] == {
            'natal_palace': natal[flow['index']]['name'], 'branch': natal[flow['index']]['earthlyBranch']}
        for star in flow['mutagen']:
            assert (star['natal_palace'], star['branch']) == positions[star['star']]
    stars = [s['name'] for p in f['yearly']['stars'] for s in p['stars']]
    assert {'流昌', '流曲', '流禄', '流羊', '流陀', '流魁', '流钺', '流马'} <= set(stars)
    assert len(f['yearly']['yearlyDecStar']['suiqian12']) == 12


def test_ziwei_horoscope_readme_fixture_matches_public_api():
    # iztro npm README.md "Quick Start": bySolar('2000-8-16', 2, '女', true, 'zh-CN').
    # Package has no shipped horoscope test fixtures: compare its public API on this
    # documented birth fixture, without claiming independently published flow values.
    js = """const {astro}=require('iztro');
astro.config({yearDivide:'normal',horoscopeDivide:'normal',dayDivide:'forward'});
console.log(JSON.stringify(astro.bySolar('2000-8-16',2,'女',true,'zh-CN').horoscope('2023-8-28',3).toJSON()));"""
    p = subprocess.run(['node', '-e', js], cwd=ROOT/'eastern/ziwei/js', text=True,
                       capture_output=True, check=True)
    reference = json.loads(p.stdout)
    r = cli('horoscope', '--birth-date', '2000-08-16', '--time', '04:00',
            '--place', '北京', '--gender', 'female', '--date', '2023-08-28', '--hour', '6')
    for key, flow in r['flows'].items():
        for field in ('name', 'index', 'heavenlyStem', 'earthlyBranch'):
            assert flow[field] == reference[key][field]
        assert [s['star'] for s in flow['mutagen']] == reference[key]['mutagen']
    assert r['flows']['age']['nominalAge'] == 24


def test_ziwei_horoscope_hour_boundaries_and_daily_calendar():
    for hour, index in ((0, 0), (1, 1), (22, 11), (23, 12)):
        r = cli('horoscope', '--person', 'S01', '--date', '2026-08-28', '--hour', str(hour))
        assert r['target']['timeIndex'] == index
        assert r['flows']['hourly']['earthlyBranch'] == '子丑寅卯辰巳午未申酉戌亥'[index % 12]
        # iztro forward late-zi day boundary matches lunar-python exact day sect 1.
        expected = Solar.fromYmdHms(2026, 8, 28, hour, 0, 0).getLunar().getDayInGanZhiExact()
        day = r['flows']['daily']
        assert day['heavenlyStem'] + day['earthlyBranch'] == expected


def test_ziwei_horoscope_approx_and_solar():
    r = cli('horoscope', '--person', 'S02', '--date', '2026-08-28')
    chart = cli('chart', '--person', 'S02')
    assert [b['candidate'] for b in r['branches']] == [b['candidate'] for b in chart['branches']]
    assert r['input']['date'] == '1975-11-02' and r['input']['time'] is None
    assert r['invariants']['不随时间变化']['yearly_干支'] == ['丙', '午']
    assert 'yearly_四化落宫' in r['invariants']['随时间变化']
    solar = cli('horoscope', '--person', 'S01', '--date', '2026-08-28', '--time-standard', 'true-solar')
    assert solar['input']['time'] == '08:45'
    assert 'solar_time' in solar['candidate']


def test_ziwei_horoscope_lunar_year_boundary():
    # lunar-python Chinese calendar: 2026 Spring Festival is February 17.
    for date, ganzhi in (('2026-02-16', '乙巳'), ('2026-02-17', '丙午')):
        r = cli('horoscope', '--person', 'S01', '--date', date)
        flow = r['flows']['yearly']
        assert flow['heavenlyStem'] + flow['earthlyBranch'] == ganzhi


def test_ziwei_horoscope_invalid_inputs():
    for extra in ([], ['--date', '2026-02-30'], ['--date', '2026-08-28', '--hour', '24']):
        p = subprocess.run([str(ROOT/'bin/prophet'), 'ziwei', 'horoscope', '--person', 'S01', *extra],
                           cwd=ROOT, text=True, capture_output=True)
        assert p.returncode != 0
        assert 'error' in json.loads(p.stdout)


def test_ziwei_horoscope_chart_rules_cache_compatibility():
    from tests.schema import check_schema
    check_schema(cli('chart', '--person', 'S01'), 'ziwei')


def test_ziwei_horoscope_missing_star_and_childhood():
    # Adapter contract for missing natal stars: retain star identity and null location.
    js = """import {astro} from 'iztro'; import {horoscope} from './horoscope.ts';
astro.config({yearDivide:'normal',horoscopeDivide:'normal',dayDivide:'forward'});
const raw=astro.bySolar('1990-3-15',4,'男',true,'zh-CN');
for(const p of raw.palaces) for(const key of ['majorStars','minorStars','adjectiveStars'])
  p[key]=p[key].filter(s=>s.name!=='文昌');
console.log(JSON.stringify(horoscope(raw,'2026-8-28')));"""
    p = subprocess.run(['node', '--import', 'tsx', '--input-type=module', '-e', js],
                       cwd=ROOT/'eastern/ziwei/js', capture_output=True, text=True, check=True)
    stars = json.loads(p.stdout)['flows']['yearly']['mutagen']
    missing = next(s for s in stars if s['star'] == '文昌')
    assert missing['natal_palace'] is None and missing['branch'] is None and missing['note']
    child = cli('horoscope', '--person', 'S01', '--date', '1990-08-28')['flows']
    assert child['age']['nominalAge'] == 1
    assert child['decadal']['childhood'] and child['decadal']['age_range'] is None
