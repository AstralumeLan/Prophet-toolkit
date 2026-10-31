"""Offline references: frozen MIT chinese-fortune tables and public-domain corpus.

No internet or external reference implementation is used by production code.
"""
import json
from pathlib import Path
import subprocess

from eastern._shensha import detect, TABLES, DAY_SETS, VARIANTS
from tests.test_bazi import invoke, example


def pillars(year='甲子', month='丙寅', day='甲子', hour='乙丑'):
    return {k: {'ganzhi': v} for k, v in zip(('year','month','day','hour'), (year,month,day,hour))}


def positions(chart, name):
    return {(p, h['hit']) for h in detect(chart, 'male') if h['name']==name for p in h['pillars']}


def test_bazi_shensha_tianyi_reference():
    # chinese-fortune/assets/shensha.json, 天乙口诀；庚辛同虎马 is a variant.
    expected = dict(zip('甲乙丙丁戊己庚辛壬癸', ('丑未','子申','亥酉','亥酉','丑未','子申','丑未','寅午','卯巳','卯巳')))
    for stem, targets in expected.items():
        assert set(TABLES['天乙贵人'][stem])==set(targets)
        for b in '子丑寅卯辰巳午未申酉戌亥':
            c=pillars(day=stem+('子' if '甲丙戊庚壬'.find(stem)>=0 else '丑'), hour='甲'+b)
            assert (('hour',b) in positions(c,'天乙贵人')) == (b in targets)
    assert any('庚辛' in v for v in VARIANTS['天乙贵人'])


def test_bazi_shensha_sanhe_reference():
    # 三命通会 sanming:c003:p0004 (马), c002:p0039 (华盖/将星).
    for branch in '申子辰':
        c=pillars(year='甲'+branch, hour='壬寅')
        assert ('hour','寅') in positions(c,'驿马')
        c['hour']['ganzhi']='癸酉'
        assert ('hour','酉') in positions(c,'桃花(咸池)')
    for branch in '寅午戌':
        c=pillars(year='甲'+branch, hour='壬申')
        assert ('hour','申') in positions(c,'驿马')
        c['hour']['ganzhi']='壬戌'
        assert ('hour','戌') in positions(c,'华盖')
    # Default deliberately uses year alone; legacy output still checks both.
    assert ('hour','申') not in positions(pillars(year='甲子',day='甲寅',hour='壬申'),'驿马')


def test_bazi_shensha_day_sets_reference():
    # Frozen vendor bazi_shensha.py constants and assets/shensha.json.
    refs={
        '魁罡': '庚辰 庚戌 壬辰 戊戌',
        '十恶大败': '甲辰 乙巳 丙申 丁亥 戊戌 己丑 庚辰 辛巳 壬申 癸亥',
        '阴差阳错': '丙子 丁丑 戊寅 辛卯 壬辰 癸巳 丙午 丁未 戊申 辛酉 壬戌 癸亥',
    }
    # yuanhai:c050:p0003 transcribes 乙丑; selected 己丑 is explicit in source.note.
    for name, text in refs.items():
        expected=set(text.split())
        assert set(DAY_SETS[name])==expected
        for i in range(60):
            day='甲乙丙丁戊己庚辛壬癸'[i%10]+'子丑寅卯辰巳午未申酉戌亥'[i%12]
            assert bool(positions(pillars(day=day),name)) == (day in expected)


def test_bazi_shensha_season_month_reference():
    # 渊海子平 论天赦 yuanhai:c036:p0003; 天德 c030:p0003.
    for months, day in [('寅卯辰','戊寅'),('巳午未','甲午'),('申酉戌','戊申'),('亥子丑','甲子')]:
        for month in months:
            assert ('day',day) in positions(pillars(month='甲'+month,day=day),'天赦')
            assert not positions(pillars(month='甲'+month,day='乙丑'),'天赦')
    assert ('hour','丁') in positions(pillars(hour='丁卯'),'天德贵人')
    # chinese-fortune 月德表: 寅午戌→丙.
    for month in '寅午戌':
        assert ('hour','丙') in positions(pillars(month='甲'+month,hour='丙子'),'月德贵人')


def test_bazi_shensha_year_reference():
    # chinese-fortune 红鸾逆行表与孤辰寡宿方局表.
    zhi='子丑寅卯辰巳午未申酉戌亥'
    for i, b in enumerate(zhi):
        target=zhi[(3-i)%12]
        assert ('hour',target) in positions(pillars(year=('甲' if i%2==0 else '乙')+b,hour='乙'+target),'红鸾')
    for b in '亥子丑':
        assert ('hour','寅') in positions(pillars(year=('甲' if zhi.index(b)%2==0 else '乙')+b,hour='丙寅'),'孤辰')
        assert ('hour','戌') in positions(pillars(year=('甲' if zhi.index(b)%2==0 else '乙')+b,hour='丙戌'),'寡宿')


def test_bazi_shensha_vendor_full_chart_overlap():
    # Execute the frozen MIT reference unmodified, in its own interpreter.
    # Intentional differences outside the comparison: 福星 uses a different
    # published mnemonic, 元辰 is gender-sensitive rather than fixed 大耗.
    script = '''import sys,json
sys.path.insert(0,'vendor/chinese-fortune/scripts')
from bazi_shensha import detect_all_shensha
p=json.loads(sys.argv[1]); s={k:v['ganzhi'][0] for k,v in p.items()}; b={k:v['ganzhi'][1] for k,v in p.items()}
data=json.load(open('vendor/chinese-fortune/assets/shensha.json'))
print(json.dumps(detect_all_shensha(data,s['day'],b['day'],p['day']['ganzhi'],s['year'],b['year'],b['month'],s,b,'male'),ensure_ascii=False))
'''
    aliases={'文昌贵人':'文昌','国印贵人':'国印','天厨贵人':'天厨','桃花咸池':'桃花(咸池)',
             '空亡':'空亡(旬空)','天罗':'天罗地网','地网':'天罗地网'}
    overlap=set(TABLES)-{'福星贵人','血刃','流霞','禄神'}
    overlap={aliases.get(n,n) for n in overlap}|{'红艳','魁罡','阴差阳错','十恶大败','空亡(旬空)','天罗地网'}
    overlap.discard('红艳煞')
    for chart in (example()['pillars'],invoke('chart','--person','S01')['candidates'][0]['pillars']):
        ref=json.loads(subprocess.check_output(['.venv/bin/python','-c',script,json.dumps(chart)],text=True))
        expected={(aliases.get(h['name'],h['name']),h['source_pillar'],h['hit']) for h in ref
                  if aliases.get(h['name'],h['name']) in overlap}
        actual={(h['name'],p,h['hit']) for h in detect(chart,'male') if h['name'] in overlap for p in h['pillars']}
        assert actual==expected, (actual-expected,expected-actual)


def test_bazi_shensha_cache_schema_and_metadata():
    from tests.schema import check_schema, schema
    out=invoke('chart','--person','S01')
    check_schema(out, 'bazi')
    assert sorted(out['candidates'][0]) == schema('bazi')['candidate']
    assert all(sorted(h) == schema('bazi')['shensha'] for h in out['candidates'][0]['shensha'])
    c=out['candidates'][0]
    for h in c['shensha_full']:
        assert h['pillars'] and set(h['pillars'])<=set(c['pillars'])
        assert h['basis'] and h['rule'] and h['source']['book'] and h['source']['note']
        assert isinstance(h['school_variants'],list)
    approx=invoke('chart','--person','S02','--time-standard','clock')
    assert all('shensha_full' in c for c in approx['candidates'])
    assert approx['shensha_full_invariants']
    assert 'shensha_full' in out['rules_ext']


def test_bazi_shensha_additional_reference_tables():
    # 通行十灵/六秀日、金神三时、空亡六旬表；explicit simplified schools.
    assert DAY_SETS['十灵']==('甲辰 乙亥 丙辰 丁酉 戊午 庚戌 庚'+'寅 辛亥 壬寅 癸未').split()
    assert DAY_SETS['六秀']=='丙午 丁未 戊子 戊午 己丑 己未'.split()
    for day in DAY_SETS['十灵']:
        assert ('day',day) in positions(pillars(day=day),'十灵')
    for hour in ('乙丑','己巳','癸酉'):
        assert ('hour',hour) in positions(pillars(hour=hour),'金神')
    assert ('hour','戌') in positions(pillars(day='甲子',hour='甲戌'),'空亡(旬空)')
    assert not positions(pillars(day='甲子',hour='甲申'),'空亡(旬空)')
    # Unknown gender must not silently select a male/female school.
    assert not any(h['name'] in ('元辰(大耗)','勾绞','天罗地网') for h in detect(pillars()))
