"""Offline Bazi calculations using 6tail lunar-python; no interpretation scoring."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from importlib.metadata import version

from lunar_python import Solar
from lunar_python.util import LunarUtil as U
from core.inputs import add_birth_args, resolve_birth, shichen_candidates, invariants
from core.solartime import true_solar
from eastern._shensha import detect as shensha_full, RULES_EXT

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'


def solar(dt):
    return Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def shensha(pillars):
    """Selected traditional lookup conventions; hits are not predictions."""
    day = pillars['day']['ganzhi']; year = pillars['year']['ganzhi']
    stems = {k: v['ganzhi'][0] for k, v in pillars.items()}
    branches = {k: v['ganzhi'][1] for k, v in pillars.items()}
    i = GAN.index(day[0]); targets = [
        ('天乙贵人', ['丑未','子申','亥酉','亥酉','丑未','子申','丑未','寅午','卯巳','卯巳'][i], '日干'),
        ('文昌', '巳午申酉申酉亥子寅卯'[i], '日干'),
        ('禄神', '寅卯巳午巳午申酉亥子'[i], '日干'),
        ('羊刃', '卯寅午巳午巳酉申子亥'[i], '日干（阴干逆行帝旺）')]
    for source, branch in [('年支', year[1]), ('日支', day[1])]:
        group = next(j for j, g in enumerate(['申子辰','寅午戌','亥卯未','巳酉丑']) if branch in g)
        for name, values in [('桃花/咸池','酉卯子午'), ('驿马','寅申巳亥'), ('华盖','辰戌未丑')]:
            targets.append((name, values[group], source))
    month = branches['month']
    targets.append(('天德', '丁申壬辛亥甲癸寅丙乙巳庚'['寅卯辰巳午未申酉戌亥子丑'.index(month)], '月支'))
    group = next(j for j, g in enumerate(['寅午戌','申子辰','亥卯未','巳酉丑']) if month in g)
    targets.append(('月德', '丙壬甲庚'[group], '月支三合'))
    hits = []
    for name, target, source in targets:
        for k in pillars:
            values = stems[k] + branches[k] if name == '天德' else stems[k] if name == '月德' else branches[k]
            for value in values:
                if value in target:
                    hits.append(dict(name=name, pillar=k, hit=value, trigger=source))
    return hits


def calculate(clock, birth, rules):
    correction = true_solar(clock, birth['lon'], birth['tz'])
    adjusted = datetime.strptime(correction['真太阳时'], '%Y-%m-%d %H:%M:%S')
    chosen = adjusted if rules['time_standard'] == 'true-solar' else clock
    # Solar terms in lunar-python are Beijing civil instants, independent of longitude.
    beijing = clock.replace(tzinfo=ZoneInfo(birth['tz'])).astimezone(ZoneInfo('Asia/Shanghai')).replace(tzinfo=None)
    lunar = solar(beijing).getLunar()
    calendar = lunar.getEightChar(); calendar.setSect(rules['sect'])
    ec = solar(chosen).getLunar().getEightChar(); ec.setSect(rules['sect'])
    ce = solar(clock).getLunar().getEightChar(); ce.setSect(rules['sect'])
    pillars = {}
    for key, prefix in [('year','Year'),('month','Month'),('day','Day'),('hour','Time')]:
        obj = calendar if key in ('year','month') else ec
        gz = getattr(obj, 'get'+prefix)()
        if key == 'year' and rules['year_boundary'] == 'spring-festival':
            gz = lunar.getYearInGanZhi()
        hidden = list(U.ZHI_HIDE_GAN[gz[1]])
        dm = ec.getDayGan()
        pillars[key] = dict(ganzhi=gz, stem=gz[0], branch=gz[1], hidden_stems=hidden,
            stem_ten_god=U.SHI_SHEN[dm+gz[0]],
            hidden_ten_gods=[U.SHI_SHEN[dm+h] for h in hidden],
            nayin=U.NAYIN[gz], xunkong=U.getXunKong(gz),
            twelve_changsheng=ec.CHANG_SHENG[({'甲':1,'乙':6,'丙':10,'丁':9,'戊':10,'己':9,'庚':7,'辛':0,'壬':4,'癸':3}[dm] + (ZHI.index(gz[1]) if GAN.index(dm)%2==0 else -ZHI.index(gz[1]))) % 12])
    counts = dict.fromkeys('木火土金水', 0)
    hidden_counts = dict.fromkeys(counts, 0)
    for p in pillars.values():
        counts[U.WU_XING_GAN[p['stem']]] += 1
        counts[U.WU_XING_ZHI[p['branch']]] += 1
        for h in p['hidden_stems']:
            hidden_counts[U.WU_XING_GAN[h]] += 1
    warnings = []
    if ce.getTime() != solar(adjusted).getLunar().getEightChar().getTime():
        warnings.append('真太阳时与钟表时间时柱不同')
    if min(abs(chosen.hour*60+chosen.minute-t) for t in (0,1380,1440)) <= 60:
        warnings.append('接近23:00换日/子时边界；请比较sect=1与sect=2')
    near = []
    for name, term in lunar.getJieQiTable().items():
        t = datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
        if abs((t-beijing).total_seconds()) <= 7200:
            near.append(dict(name=name, exact_time=t.isoformat(' '), tz='Asia/Shanghai'))
    if near:
        warnings.append('出生在节气交接前后两小时内')
    yun_data = None
    if birth['gender']:
        forward = (GAN.index(pillars['year']['stem']) % 2 == 0) == (birth['gender'] == 'male')
        # Library's Yun uses its own Li-Chun year. Select equivalent direction when year rule differs.
        lib_yang = GAN.index(calendar.getYearGan()) % 2 == 0
        gender_for_direction = int(lib_yang == forward)
        yun = calendar.getYun(gender_for_direction, rules['yun_sect'])
        steps = [dict(ganzhi=d.getGanZhi(), start_year=d.getStartYear(), end_year=d.getEndYear(),
                      start_age=d.getStartAge(), end_age=d.getEndAge()) for d in yun.getDaYun(11)[1:]]
        yun_data = dict(direction='forward' if forward else 'backward', start_date=yun.getStartSolar().toYmdHms(), start_date_tz='Asia/Shanghai',
                        start_age=dict(years=yun.getStartYear(), months=yun.getStartMonth(), days=yun.getStartDay(), hours=yun.getStartHour()),
                        age_convention='大运start_age/end_age为lunar-python虚岁；起运间隔另列', steps=steps)
    else:
        warnings.append('未提供性别，无法确定大运顺逆及起运')
    return dict(pillars=pillars, year_pillar=pillars['year']['ganzhi'], month_pillar=pillars['month']['ganzhi'],
                day_pillar=pillars['day']['ganzhi'], hour_pillar=pillars['hour']['ganzhi'], day_master=ec.getDayGan(),
                clock_time=clock.isoformat(' '), true_solar=correction, calculation_time=chosen.isoformat(' '),
                clock_hour_pillar=ce.getTime(), true_solar_hour_pillar=solar(adjusted).getLunar().getEightChar().getTime(),
                hour_pillars_differ=ce.getTime()!=solar(adjusted).getLunar().getEightChar().getTime(),
                shensha=shensha(pillars), shensha_full=shensha_full(pillars, birth['gender']),
                five_elements=counts, hidden_stem_elements=hidden_counts,
                dayun=yun_data, taiyuan=ec.getTaiYuan(), minggong=ec.getMingGong(), nearby_solar_terms=near, warnings=warnings)


def run(args):
    b = resolve_birth(args)
    if b['时间精度']['类型'] == 'unknown':
        raise ValueError('八字需要出生时间或 --time-range；不使用中午占位排盘')
    rules = dict(sect=args.sect, year_boundary=args.year_boundary, month_boundary=args.month_boundary,
                 time_standard=args.time_standard, yun_sect=args.yun_sect,
                 calendar='lunar-python; 节气按Asia/Shanghai绝对时刻，日时按所选时间标准',
                 shensha_source='渊海子平通行神煞歌诀；参考vendor/chinese-fortune/scripts/bazi_shensha.py；年/日支均查桃花驿马华盖；日干查贵人文昌禄刃',
                 element_count='四干四支各计一次；藏干另外不加权计数', operation=args.bazi_command,
                 forecast_year=getattr(args, 'year', None))
    results = []
    candidates = shichen_candidates(b, true_solar=args.time_standard == 'true-solar')
    # A single 子时 may straddle midnight; a single 时辰 may straddle a 节气.
    # Retain additional boundary samples when their actual pillar signatures differ.
    if b.get('range_dt'):
        start, end = b['range_dt']
        extra = [start, end]
        for y in range(start.year-1, end.year+2):
            for term in solar(datetime(y, 6, 1)).getLunar().getJieQiTable().values():
                bj = datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
                local = bj.replace(tzinfo=ZoneInfo('Asia/Shanghai')).astimezone(ZoneInfo(b['tz'])).replace(tzinfo=None)
                extra.extend([local-timedelta(seconds=1), local])
        day = start.replace(hour=0, minute=0, second=0)
        while day <= end+timedelta(days=1):
            offset = datetime.strptime(true_solar(day, b['lon'], b['tz'])['真太阳时'], '%Y-%m-%d %H:%M:%S')-day
            midnight = day-offset if args.time_standard=='true-solar' else day
            extra.extend([midnight-timedelta(seconds=1), midnight, midnight+timedelta(seconds=1)])
            day += timedelta(days=1)
        existing = [calculate(c['dt'], b, rules) for c in candidates]
        keys = ('year_pillar','month_pillar','day_pillar','hour_pillar','clock_hour_pillar')
        signatures = {tuple(c[k] for k in keys) for c in existing}
        for dt in sorted(set(t for t in extra if start<=t<=end)):
            chart = calculate(dt, b, rules)
            signature = tuple(chart[k] for k in keys)
            if signature not in signatures:
                signatures.add(signature)
                candidates.append(dict(dt=dt, label='日界/节气/区间端点候选', kind='boundary-sample', note='计算样本，非确认出生时间'))
    for candidate in candidates:
        chart = calculate(candidate['dt'], b, rules)
        if args.bazi_command == 'liunian':
            gz = Solar.fromYmdHms(args.year, 7, 1, 12, 0, 0).getLunar().getYearInGanZhiExact()
            chart['liunian'] = dict(year=args.year, ganzhi=gz, stem_ten_god=U.SHI_SHEN[chart['day_master']+gz[0]],
                hidden_ten_gods=[U.SHI_SHEN[chart['day_master']+h] for h in U.ZHI_HIDE_GAN[gz[1]]],
                dayun=next((d for d in (chart['dayun'] or {}).get('steps', []) if d['start_year']<=args.year<=d['end_year']), None),
                boundary='立春至次年立春；大运归属按lunar-python起止年份')
        elif args.bazi_command == 'liuyue':
            months = []
            for year in (args.year, args.year+1):
                table = Solar.fromYmdHms(year, 6, 1, 12, 0, 0).getLunar().getJieQiTable()
                names = ['立春','惊蛰','清明','立夏','芒种','小暑','立秋','白露','寒露','立冬','大雪'] if year==args.year else ['小寒']
                for name in names:
                    term=table[name]; dt=datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
                    gz=solar(dt+timedelta(seconds=1)).getLunar().getMonthInGanZhiExact()
                    months.append(dict(jie=name, start=term.toYmdHms(), tz='Asia/Shanghai', ganzhi=gz,
                                       stem_ten_god=U.SHI_SHEN[chart['day_master']+gz[0]]))
            chart['liuyue']=months
        results.append(dict(candidate=candidate, **chart))
    out = dict(engine=dict(name='eastern.bazi / lunar-python', version=version('lunar-python'), rules=rules),
               warnings=sorted(set(w for r in results for w in r['warnings'])), person=b['代号'], input=b, candidates=results,
               invariants=invariants(results, ['year_pillar','month_pillar','day_pillar','hour_pillar','day_master','five_elements','shensha','dayun'] + ([args.bazi_command] if args.bazi_command!='chart' else [])))
    if b.get('range_dt'):
        out['warnings'].append('约略时辰为计算分支；起运日期为样本值，并非已确认的精确起运时间')
    out['rules_ext'] = {'shensha_full': dict(RULES_EXT)}
    out['shensha_full_invariants'] = invariants(results, ['shensha_full'])
    if args.save_cache:
        if not args.person:
            raise ValueError('--save-cache 需要 --person')
        from core.cache import save
        out['cache_path']=save(b['代号'], 'bazi', rules, out)
    return out


from argparse import Namespace


def daily_pillar(ganzhi, day_master=None):
    """Shared lunar-python lookup tables, also used by chart/forecasts."""
    hidden = list(U.ZHI_HIDE_GAN[ganzhi[1]])
    result = dict(ganzhi=ganzhi, stem=ganzhi[0], branch=ganzhi[1],
                  nayin=U.NAYIN[ganzhi], hidden_stems=hidden)
    if day_master:
        result.update(stem_ten_god=U.SHI_SHEN[day_master+ganzhi[0]],
                      hidden_ten_gods=[U.SHI_SHEN[day_master+h] for h in hidden])
    return result


def daily(date, tz='Asia/Shanghai', sect=2, year_boundary='lichun', day_master=None):
    """Civil-date almanac: local noon for pillars; Beijing absolute JieQi.

    Twelve branches contain thirteen civil segments: 子 includes early/late 子.
    EightChar sect selects the late-子 day; lunar-python's hour stem always
    follows its 23:00 rollover, exactly as chart does (even with sect=2).
    """
    noon = datetime.strptime(date, '%Y-%m-%d').replace(hour=12)
    bj = noon.replace(tzinfo=ZoneInfo(tz)).astimezone(ZoneInfo('Asia/Shanghai')).replace(tzinfo=None)
    calendar = solar(bj).getLunar()
    lunar = solar(noon).getLunar()
    ec = lunar.getEightChar(); ec.setSect(sect)
    year = calendar.getYearInGanZhiExact() if year_boundary == 'lichun' else calendar.getYearInGanZhi()
    pillars = {key: daily_pillar(gz, day_master) for key, gz in (
        ('year', year), ('month', calendar.getMonthInGanZhiExact()), ('day', ec.getDay()))}
    hours = []
    for i, branch in enumerate(ZHI):
        segments = []
        spans = [(0, '00:00-01:00', '早子'), (23, '23:00-24:00', '晚子')] if i == 0 else [(2*i-1, f'{2*i-1:02d}:00-{2*i+1:02d}:00', branch)]
        for h, span, label in spans:
            l = solar(noon.replace(hour=h, minute=30)).getLunar()
            e = l.getEightChar(); e.setSect(sect)
            t = l.getTime()
            segments.append(dict(label=label, time_range=span,
                **daily_pillar(e.getTime(), day_master), day_ganzhi=e.getDay(),
                tianshen=t.getTianShen(), tianshen_type=t.getTianShenType(), tianshen_luck=t.getTianShenLuck()))
        hours.append(dict(branch=branch, segments=segments))
    return dict(date=date, tz=tz, reference_time=noon.isoformat(' '), pillars=pillars,
                liunian=pillars['year'], liuyue=pillars['month'], liuri=pillars['day'], hours=hours,
                day_tianshen=dict(name=lunar.getDayTianShen(), type=lunar.getDayTianShenType(), luck=lunar.getDayTianShenLuck()))


def run_daily(args):
    # --date is the target; never pass it through as a person's birth override.
    if not args.date:
        raise ValueError('daily 需要 --date YYYY-MM-DD')
    natal = None
    if args.person or args.birth_date:
        birth_args = Namespace(**vars(args))
        birth_args.date = args.birth_date
        birth_args.bazi_command = 'chart'
        birth_args.save_cache = False
        natal = run(birth_args)
    elif args.time or args.time_range:
        raise ValueError('临时出生输入需要 --birth-date；--date 是查询日期')
    tz = args.tz or (natal['input']['tz'] if natal else 'Asia/Shanghai')
    out = dict(engine=dict(name='eastern.bazi / lunar-python', version=version('lunar-python'),
                          rules=dict(operation='daily', sect=args.sect, year_boundary=args.year_boundary,
                                     month_boundary=args.month_boundary)), warnings=[],
               rules_ext=dict(reference='目标日期当地钟表中午12:00定年月日；年月节气按北京时间绝对时刻；不作真太阳时校正',
                              zi='子分早子/晚子；sect同chart；时干及十二神依lunar-python，23:00起次日时干/十二神，sect=2仅日柱不换日',
                              dayun='沿用chart大运起止公历年份；首运须已到精确起运时刻；后续交运不推算精确月日'))
    if not natal:
        out.update(daily(args.date, tz, args.sect, args.year_boundary))
        return out
    out.update(person=natal['person'], input=natal['input'])
    out['warnings'] = list(natal['warnings'])
    target = datetime.strptime(args.date, '%Y-%m-%d').replace(hour=12, tzinfo=ZoneInfo(tz))
    personal = []
    for c in natal['candidates']:
        yun = c['dayun']
        active = None
        if yun and target >= datetime.strptime(yun['start_date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo('Asia/Shanghai')):
            active = next((d for d in yun['steps'] if d['start_year'] <= target.year <= d['end_year']), None)
        personal.append(dict(candidate=c['candidate'], day_master=c['day_master'], active_dayun=active))
    masters = list(dict.fromkeys(c['day_master'] for c in personal))
    out['birth_candidates'] = personal
    out['invariants'] = invariants(personal, ['day_master', 'active_dayun'])
    if len(masters) == 1:
        out.update(daily(args.date, tz, args.sect, args.year_boundary, masters[0]))
        out['day_master'] = masters[0]
        out['active_dayun'] = out['invariants']['不随时间变化'].get('active_dayun')
    else:
        out['candidates'] = [dict(day_master=dm, **daily(args.date, tz, args.sect, args.year_boundary, dm)) for dm in masters]
        out['warnings'].append('出生日主随候选时间变化；日运十神按日主分支')
    if natal['input'].get('range_dt'):
        out['warnings'].append('大运起运保留出生时间候选；不将取样时间视为确认生时')
    return out


def register(subparsers):
    parser=subparsers.add_parser('bazi', help='八字四柱、大运、流年流月')
    sub=parser.add_subparsers(dest='bazi_command', required=True)
    for command in ('chart','liunian','liuyue'):
        p=sub.add_parser(command); add_birth_args(p)
        p.add_argument('--sect', type=int, choices=(1,2), default=2)
        p.add_argument('--year-boundary', choices=('lichun','spring-festival'), default='lichun')
        p.add_argument('--month-boundary', choices=('jieqi',), default='jieqi')
        p.add_argument('--time-standard', choices=('true-solar','clock'), default='true-solar')
        p.add_argument('--yun-sect', type=int, choices=(1,2), default=1)
        p.add_argument('--save-cache', action='store_true')
        if command!='chart':
            p.add_argument('--year', type=int, required=True)
        p.set_defaults(func=run)

    p=sub.add_parser('daily', help='日运：当地中午年月日柱、十二时辰与值神')
    add_birth_args(p)
    p.add_argument('--birth-date', help='临时出生日期；--date 专用于查询日期')
    p.add_argument('--sect', type=int, choices=(1,2), default=2)
    p.add_argument('--year-boundary', choices=('lichun','spring-festival'), default='lichun')
    p.add_argument('--month-boundary', choices=('jieqi',), default='jieqi')
    p.add_argument('--time-standard', choices=('true-solar','clock'), default='true-solar', help='仅用于出生盘')
    p.add_argument('--yun-sect', type=int, choices=(1,2), default=1)
    p.set_defaults(func=run_daily)
