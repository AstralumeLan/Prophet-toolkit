"""Offline Ziwei bridge: iztro plus the MIT Renhuai chart adapter."""
from __future__ import annotations
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from core.inputs import add_birth_args, resolve_birth, shichen_candidates, invariants
from core.solartime import true_solar

JS = Path(__file__).resolve().parent / 'js'


def run(args):
    if args.sub == 'horoscope':
        from argparse import Namespace
        if not args.date:
            raise ValueError('ziwei horoscope 需要 --date YYYY-MM-DD 目标日期')
        datetime.strptime(args.date, '%Y-%m-%d')
        if args.hour is not None and not 0 <= args.hour <= 23:
            raise ValueError('--hour 必须在 0–23 之间')
        birth = resolve_birth(Namespace(**{**vars(args), 'date': args.birth_date}))
    else:
        birth = resolve_birth(args)
    if not birth['gender']:
        raise ValueError('紫微排盘需要 --gender male/female')
    if birth['时间精度']['类型'] == 'unknown':
        raise ValueError('紫微排盘需要时间或 --time-range；不能使用未知时间的中午占位')
    solar = args.time_standard == 'true-solar'
    candidates = shichen_candidates(birth, true_solar=solar)
    # 子时 spans midnight; split it because early/late zi imply different chart dates.
    if birth.get('range_dt'):
        start, end = birth['range_dt']
        segments = []
        t = start
        while t <= end:
            dt = datetime.strptime(true_solar(t,birth['lon'],birth['tz'])['真太阳时'], '%Y-%m-%d %H:%M:%S') if solar else t
            key = (dt.date(), 12 if dt.hour == 23 else (dt.hour+1)//2)
            if segments and segments[-1][0] == key:
                segments[-1][2] = t
            else:
                segments.append([key,t,t])
            t += timedelta(minutes=1)
        if len(segments) != len(candidates):
            candidates = [{'label':f'{s:%Y-%m-%d %H:%M}–{e:%Y-%m-%d %H:%M}',
                'dt':s, 'kind':'shichen-sample', 'clock_span':[str(s),str(e)],
                'note':'计算取样点，非确认出生时间'} for _,s,e in segments]
    requests=[]
    for c in candidates:
        dt=c['dt']
        correction=true_solar(dt,birth['lon'],birth['tz']) if solar else None
        used=datetime.strptime(correction['真太阳时'],'%Y-%m-%d %H:%M:%S') if solar else dt
        c['computed_time']=str(used)
        if correction:
            c['solar_time']=correction
        requests.append(dict(date=used.strftime('%Y-%m-%d'),hour=used.hour,minute=used.minute,
            gender=birth['gender'],year=args.year,school=args.school,leapMonth=args.leap_month))
    if args.sub == 'horoscope':
        for request in requests:
            request.update(command='horoscope', targetDate=args.date, targetHour=args.hour)
    proc=subprocess.run(['node','--import','tsx',str(JS/'cli.ts')],
        input=json.dumps({'candidates':requests},ensure_ascii=False),text=True,capture_output=True,cwd=JS,timeout=30)
    try:
        data=json.loads(proc.stdout)
    except ValueError as exc:
        raise RuntimeError(f'Ziwei Node bridge failed: {proc.stderr[-1000:]}') from exc
    if proc.returncode or 'error' in data:
        raise RuntimeError(data.get('error',proc.stderr[-1000:]))
    rules={'time_standard':args.time_standard,'late_zi':'23:00 next-day; iztro index 12, Renhuai next-date index 0',
        'yearDivide':'lunar-new-year','brightness_school':args.school,'leap_month':args.leap_month,
        'annual_reference':'July 1 of requested year; lunar-year horoscope',
        'four_pillars':'Renhuai uses shichen representative hours, not exact birth minutes'}
    warnings=['Renhuai internally uses iztro; agreement is not independent verification.']
    if birth.get('range_dt'):
        warnings.append('约略时间按时辰分支；取样时刻不是确认出生时间。')
    if birth['时间精度']['类型']=='provisional':
        warnings.append('出生时间为暂用值。')
    out={'engine':{'name':'prophet.ziwei','version':'1.0.0','rules':rules},'warnings':warnings,'input':birth}
    results=data['results']
    if args.sub == 'horoscope':
        out['engine'] = {'name':'prophet.ziwei.horoscope', 'version':'1.0.0', 'rules':{
            'time_standard':args.time_standard, 'yearDivide':'normal (lunar-new-year)',
            'horoscopeDivide':'normal (lunar year/month)', 'dayDivide':'forward (23:00 next-day ganzhi)',
            'ageDivide':'normal (nominal age changes at lunar new year)',
            'leap_month':args.leap_month, 'flow_leap_month':'iztro split at day 15', 'target_time':'local civil date/hour; no solar correction',
            'target_hour_omitted':'index 0 internally; hourly omitted',
            'palace_indices':'iztro natal order starting at 寅; palace_names maps flow names to natal palaces'}}
        out['warnings'] = [w for w in warnings if not w.startswith('Renhuai internally')]
        if birth.get('range_dt'):
            out['branches'] = [{'candidate':c, **r} for c,r in zip(candidates,results)]
            summaries = []
            for r in results:
                summary = {}
                for key, flow in r['flows'].items():
                    summary[key + '_干支'] = [flow['heavenlyStem'], flow['earthlyBranch']]
                    summary[key + '_四化落宫'] = flow['mutagen']
                    summary[key + '_流宫'] = flow['palace_names']
                summaries.append(summary)
            out['invariants'] = invariants(summaries)
        else:
            out.update(candidate=candidates[0], **results[0])
        return out
    if args.sub == 'compare':
        out.update(agree=all(r['comparison']['agree'] for r in results),
                   diffs=[dict(candidate=c['label'],**d) for c,r in zip(candidates,results) for d in r['comparison']['diffs']])
    if birth.get('range_dt'):
        out['branches']=[{'candidate':c,**r} for c,r in zip(candidates,results)]
        summaries=[]
        for r in results:
            ch=r['renhuai']; ming=next(p for p in ch['palaces'] if p['name']=='命宫')
            summaries.append({'命宫地支':ch['mingGongBranch'], '命宫主星':[s['name'] for s in ming['stars'] if s['type']=='major'],
                '五行局':ch['wuxingJuName'],'生年四化星':sorted((s['star'],s['transformation']) for s in r['sihua'])})
        out['invariants']=invariants(summaries)
    else:
        out.update(candidate=candidates[0],**results[0])
    if args.save_cache:
        if not birth['代号']:
            raise ValueError('--save-cache 需要 --person')
        from core.cache import save
        out['cache_path']=save(birth['代号'],'ziwei',dict(rules,year=args.year,command=args.sub),out)
    return out


def register(subparsers):
    p=subparsers.add_parser('ziwei',help='紫微斗数：iztro + Renhuai（离线）')
    subs=p.add_subparsers(dest='sub',required=True)
    for name in ('chart','compare'):
        q=subs.add_parser(name)
        add_birth_args(q)
        q.add_argument('--year',type=int,help='流年（以该年7月1日的农历年为准）')
        q.add_argument('--time-standard',choices=['clock','true-solar'],default='clock')
        q.add_argument('--school','--brightness-school',choices=['default','QS','XD1','ZZ','XD2'],default='default')
        q.add_argument('--leap-month',choices=['split','prev-month','next-month','origin-month'],default='split')
        q.add_argument('--save-cache',action='store_true')
        q.set_defaults(func=run)

    q = subs.add_parser('horoscope', help='大限、小限及流年/月/日/时；--date 为目标日')
    add_birth_args(q)
    # Reuse shared birth flags but reserve --date for the target, never a birth override.
    date_action = next(a for a in q._actions if a.dest == 'date')
    date_action.help = '目标日期 YYYY-MM-DD（非出生日期）'
    q.add_argument('--birth-date', help='临时出生日期 YYYY-MM-DD；--person 时默认档案日期')
    q.add_argument('--hour', type=int, help='目标钟表小时0–23；省略不输出流时')
    q.add_argument('--time-standard', choices=['clock','true-solar'], default='clock')
    q.add_argument('--leap-month', choices=['split','prev-month','next-month','origin-month'], default='split')
    q.set_defaults(func=run, year=None, school='default', save_cache=False)
