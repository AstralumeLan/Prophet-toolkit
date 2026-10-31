"""Offline, in-process cross checks with concrete differences and declared rules."""
from argparse import Namespace
from datetime import timedelta
from core.inputs import add_birth_args, resolve_birth, shichen_candidates, sample_candidates, invariants
from validate.ziwei_indep import calculate, RULES

ENGINE = {'name':'validate.cross','version':'1.0.0','rules':{
    'birth_time':'clock; no true-solar substitution', 'bazi':'lunar-python sect 2, lichun vs iztro normal lunar-new-year; iztro hour index 0–12 (23h=12), forward day',
    'ziwei_independent':RULES,'western_tolerance_arcmin':'Sun–Saturn including Moon: 1; Uranus–Pluto: 2',
    'gender':'when absent, female supplied only to ziwei adapter; all compared fields are gender-independent',
    'vedic':'astronomy-engine tropical minus Swiss Lahiri; independent nakshatra/pada arithmetic; nodes excluded'}}


def difference(field, a, b):
    return {'field':field,'engine_a':a,'engine_b':b}


def result(diffs, **extra):
    return {'agree':not diffs,'diff':diffs, **extra}


def ziwei_check(dt, raw):
    independent = calculate(dt)
    chart = raw['iztro']
    positions = {s['name']:p['earthlyBranch'] for p in chart['palaces']
                 for group in ('majorStars','minorStars','adjectiveStars') for s in p[group]}
    actual = {'positions':{s:positions.get(s) for s in independent['positions']},
              'soul':chart['earthlyBranchOfSoulPalace'],'body':chart['earthlyBranchOfBodyPalace'],
              'soul_ganzhi':next(p['heavenlyStem']+p['earthlyBranch'] for p in chart['palaces'] if p['name']=='命宫'),
              'bureau':chart['fiveElementsClass'],
              'sihua':{s['transformation']:s['star'] for s in raw['sihua']}}
    diffs = []
    for key in actual:
        if isinstance(actual[key],dict):
            for name, value in independent[key].items():
                if value != actual[key].get(name):
                    diffs.append(difference(f'{key}.{name}',actual[key].get(name),value))
        elif actual[key] != independent[key]:
            diffs.append(difference(key,actual[key],independent[key]))
    shared = [difference('major_stars.'+d['star'],d['iztro'],d['renhuai']) for d in raw['comparison']['diffs']]
    return result(diffs+shared, independent=result(diffs,chart=independent),
                  renhuai=result(shared,independent=False))


def bazi_check(dt, birth, raw):
    from eastern.bazi import calculate as bazi
    chart = bazi(dt,birth,dict(time_standard='clock',sect=2,year_boundary='lichun',month_boundary='jieqi',yun_sect=1))
    a = {k:v['ganzhi'] for k,v in chart['pillars'].items()}
    b = dict(zip(('year','month','day','hour'),raw['iztro']['chineseDate'].split()))
    return result([difference(k,a[k],b[k]) for k in a if a[k]!=b[k]],engine_a=a,engine_b=b,
                  rule_notes=[ENGINE['rules']['bazi'],'Year-boundary and late-子 day differences remain visible; iztro uses representative shichen hours, not exact solar-term minutes.'])


def longitude_check(dt, birth, vedic=False):
    import swisseph as swe
    from western.astro import jd, positions_swe, positions_alt, delta
    j = jd(dt,birth['tz'])
    alt = positions_alt(j)
    diffs, planets = [], {}
    if vedic:
        from vedic.jyotish import calculate_chart
        chart = calculate_chart(dt,birth['lat'],birth['lon'],birth['tz'],at=dt.isoformat(),levels=1)
        a = {p:v['longitude'] for p,v in chart['grahas'].items() if p in alt}
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(j)
        alt = {p:(alt[p]-ayanamsa)%360 for p in a}
    else:
        a = positions_swe(j)
    for p,b in alt.items():
        tolerance = 2 if p in ('Uranus','Neptune','Pluto') else 1
        arcmin = abs(delta(a[p]-b))*60
        item = {'engine_a':a[p],'engine_b':b,'diff_arcmin':arcmin,'tolerance_arcmin':tolerance,'agree':arcmin<=tolerance}
        if not item['agree']:
            diffs.append(difference(p+'.longitude',a[p],b)|{'diff_arcmin':arcmin,'tolerance_arcmin':tolerance})
        if vedic:
            n = chart['grahas'][p]['nakshatra']
            # Independent partition: 27 equal lunar mansions, each with four quarters.
            q = int((b%360)*108/360)
            na, nb = {'index':n['index'],'pada':n['pada']}, {'index':q//4+1,'pada':q%4+1}
            item.update(nakshatra_a=na,nakshatra_b=nb,nakshatra_agree=na==nb)
            if na!=nb:
                diffs.append(difference(p+'.nakshatra',na,nb))
            item['agree'] = item['agree'] and na==nb
        planets[p] = item
    return result(diffs,planets=planets,**({'ayanamsa':ayanamsa} if vedic else {}))


def _eastern_candidates(birth):
    candidates = shichen_candidates(birth)
    # Shared shichen helper merges 子 across midnight; preserve calendar date boundaries.
    if birth.get('range_dt'):
        start,end = birth['range_dt']
        t=start
        boundaries=[]
        while t<=end:
            if t.hour==0 and t.minute==0 and t>start:
                boundaries.append(t)
            t+=timedelta(minutes=1)
        if boundaries:
            candidates = sorted({c['dt']:c for c in candidates+[
                {'dt':t,'label':str(t),'kind':'calendar-boundary-sample'} for t in boundaries+
                [t-timedelta(minutes=1) for t in boundaries]]}.values(),key=lambda c:c['dt'])
    return candidates


def run(args):
    birth = resolve_birth(args)
    if birth['时间精度']['类型']=='unknown':
        raise ValueError('交叉校验需要 --time 或 --time-range')
    systems = ('bazi','ziwei','western','vedic') if args.validation=='all' else (args.validation,)
    eastern = _eastern_candidates(birth)
    raw_by_dt = {}
    warnings = []
    if any(s in systems for s in ('bazi','ziwei')):
        from eastern.ziwei import run as ziwei
        # Use public engine wrapper, retaining its batching and midnight splitting.
        request = vars(args).copy()
        request.update(sub='chart',time_standard='clock',year=None,school='default',leap_month='split',save_cache=False)
        # Single exact calls avoid mismatching the wrapper's internal range partitions.
        for c in eastern:
            exact = dict(request,person=None,date=c['dt'].strftime('%Y-%m-%d'),time=c['dt'].strftime('%H:%M'),time_range=None,
                         lat=birth['lat'],lon=birth['lon'],tz=birth['tz'],gender=birth['gender'] or 'female')
            raw_by_dt[c['dt']] = ziwei(Namespace(**exact))
        if 'ziwei' in systems:
            warnings.append('Renhuai wraps iztro: its comparison is not independent. Pure-Python placement is independent; the lunar calendar still uses lunar-python.')
    checks = {}
    for system in systems:
        candidates = eastern if system in ('bazi','ziwei') else sample_candidates(birth)
        branches=[]
        for c in candidates:
            dt=c['dt']
            if system=='bazi': r=bazi_check(dt,birth,raw_by_dt[dt])
            elif system=='ziwei': r=ziwei_check(dt,raw_by_dt[dt])
            else: r=longitude_check(dt,birth,system=='vedic')
            branches.append(dict(candidate=c,**r))
        aggregate = [dict(candidate=r['candidate']['label'],**d) for r in branches for d in r['diff']]
        checks[system] = result(aggregate)
        if birth.get('range_dt'):
            checks[system].update(branches=branches,invariants=invariants([{k:v for k,v in r.items() if k!='candidate'} for r in branches]))
        else:
            checks[system].update(branches[0])
    out = {'engine':ENGINE,'warnings':warnings,'input':birth}
    if birth.get('range_dt'):
        out['warnings'].append('约略时间仅取候选样本；invariants 是样本间稳定项，并非连续区间证明。')
    if args.validation=='all':
        out.update(results=checks,summary={s:{'agree':r['agree'],'n_diffs':len(r['diff'])} for s,r in checks.items()},
                   agree=all(r['agree'] for r in checks.values()))
        if birth.get('range_dt'):
            out['invariants']={s:r['invariants'] for s,r in checks.items()}
    else:
        out.update(checks[args.validation])
    return out


def register(subparsers):
    p = subparsers.add_parser('validate',help='离线交叉校验')
    sub = p.add_subparsers(dest='validation',required=True)
    for name in ('bazi','ziwei','western','vedic','all'):
        q=sub.add_parser(name)
        add_birth_args(q)
        q.set_defaults(func=run)
