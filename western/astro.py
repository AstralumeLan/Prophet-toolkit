"""Offline tropical astrology using Swiss Ephemeris and an independent validator."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import swisseph as swe
from core.inputs import add_birth_args, resolve_birth, sample_candidates, invariants

FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
EPHE_PATH = Path(__file__).resolve().parent / 'data'
CHIRON_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
CHIRON_SOURCE = 'Swiss Ephemeris seas_18.se1 (~1800–2399; availability checked by Swiss Ephemeris)'
CHIRON_STATION_THRESHOLD = 0.001  # degrees/day; numerical near-station convention
PLANETS = {n: getattr(swe, k) for n, k in [('Sun','SUN'),('Moon','MOON'),('Mercury','MERCURY'),('Venus','VENUS'),('Mars','MARS'),('Jupiter','JUPITER'),('Saturn','SATURN'),('Uranus','URANUS'),('Neptune','NEPTUNE'),('Pluto','PLUTO'),('True Node','TRUE_NODE'),('Mean Node','MEAN_NODE'),('Chiron','CHIRON')]}
SIGNS = 'Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces'.split()
HOUSES = {'placidus':b'P','whole-sign':b'W','koch':b'K','equal':b'E','porphyry':b'O'}
ORB = {'conj':8,'opp':8,'trine':6,'square':6,'sextile':4}
ANGLES = {'conj':0,'opp':180,'trine':120,'square':90,'sextile':60,'semisextile':30,'semisquare':45,'sesquisquare':135,'quincunx':150}

def delta(x):
    return (x+180)%360-180

def jd(dt, tz='UTC'):
    dt = (dt.replace(tzinfo=ZoneInfo(tz)) if dt.tzinfo is None else dt).astimezone(timezone.utc)
    return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+(dt.second+dt.microsecond/1e6)/3600)

def instant(j):
    y,m,d,h=swe.revjul(j)
    from datetime import timedelta
    return (datetime(y,m,d,tzinfo=timezone.utc)+timedelta(hours=h)).isoformat()

def positions_swe(jd_ut):
    positions = {n:swe.calc_ut(jd_ut,p,FLAGS)[0][0] for n,p in PLANETS.items() if n != 'Chiron'}
    try: positions['Chiron'] = chiron_position(jd_ut)[0]
    except swe.Error: pass
    return positions

def chiron_position(jd_ut):
    if not (EPHE_PATH / 'seas_18.se1').is_file():
        raise swe.Error('seas_18.se1 missing')
    swe.set_ephe_path(str(EPHE_PATH))
    return swe.calc_ut(jd_ut, swe.CHIRON, CHIRON_FLAGS)[0]

def positions_alt(jd_ut):
    import astronomy as a
    t=a.Time(jd_ut-2451545.0)
    return {n:a.Ecliptic(a.GeoVector(getattr(a.Body,n),t,True)).elon for n in list(PLANETS)[:10]}

def point(lon):
    return {'lon':lon%360,'sign':SIGNS[int(lon%360//30)],'degree_in_sign':lon%30}

def aspects(left,right=None,orbs=None):
    out=[]; orbs=orbs or ORB
    for i,(a,x) in enumerate(left.items()):
        for j,(b,y) in enumerate((right or left).items()):
            if right is None and j<=i: continue
            sep=abs(delta(x['lon']-y['lon']))
            for name,orb in orbs.items():
                err=abs(sep-ANGLES[name])
                if err<=orb:
                    future=abs(delta(x['lon']+x.get('speed',0)/1440-y['lon']-y.get('speed',0)/1440))
                    change=abs(future-ANGLES[name])-err
                    out.append({'a':a,'b':b,'aspect':name,'angle':ANGLES[name],'orb':err,'phase':'applying' if change< -1e-10 else 'separating' if change>1e-10 else 'stationary'})
    return out

def chart(j,lat,lon,house_system='placidus',orbs=None):
    warnings=['Main planets and lunar nodes use Moshier ephemeris.']
    actual=house_system
    if abs(lat)>=66 and actual in ('placidus','koch'):
        actual='porphyry'; warnings.append('Polar latitude: house system falls back to porphyry.')
    try: cusps,axes=swe.houses(j,lat,lon,HOUSES[actual])
    except swe.Error:
        actual='whole-sign'; cusps,axes=swe.houses(j,lat,lon,b'W'); warnings.append('House calculation failed; using whole-sign.')
    planets={}
    for n,p in PLANETS.items():
        try:
            if n == 'Chiron': v = chiron_position(j)
            else: v,flag=swe.calc_ut(j,p,FLAGS)
        except swe.Error:
            warnings.append(f'{n} unavailable with Moshier; omitted.'); continue
        h=next((i+1 for i in range(12) if (v[0]-cusps[i])%360 < (cusps[(i+1)%12]-cusps[i])%360),None)
        planets[n]={**point(v[0]),'latitude':v[1],'speed':v[3],'retrograde':v[3]<0,'house':h}
        if n == 'Chiron':
            planets[n]['stationary'] = abs(v[3]) < CHIRON_STATION_THRESHOLD
            warnings.append('Chiron uses ' + CHIRON_SOURCE + '.')
    rules={'zodiac':'tropical','ephemeris':'Moshier','house_system':actual,'requested_house_system':house_system,'orbs':orbs or ORB,'time_scale':'UT (UTC approximation)','house_assignment':'ecliptic longitude cusp intervals'}
    return {'engine':{'name':'western.astro','version':'1.0.0','rules':rules,'rules_ext':{'chiron_source':CHIRON_SOURCE,'chiron_station_threshold_deg_per_day':CHIRON_STATION_THRESHOLD}},'warnings':warnings,'jd_ut':j,'utc':instant(j),'planets':planets,'angles':{n:point(v) for n,v in [('ASC',axes[0]),('MC',axes[1]),('DSC',axes[0]+180),('IC',axes[1]+180)]},'houses':[dict(house=i+1,**point(c)) for i,c in enumerate(cusps)],'aspects':aspects(planets,orbs=orbs)}

def summary(c):
    return {**{n+' sign':p['sign'] for n,p in c['planets'].items()},**{n+' sign':p['sign'] for n,p in c['angles'].items()},'houses':{n:p['house'] for n,p in c['planets'].items()},'ASC longitude':c['angles']['ASC']['lon'],'MC longitude':c['angles']['MC']['lon']}

def run(a):
    birth_args=a
    return_geo=None
    if a.sub=='solar-return' and a.person and a.place:
        from core.geo import lookup
        return_geo=lookup(a.place)
        birth_args=SimpleNamespace(**{**vars(a),'place':None})
    b=resolve_birth(birth_args); orbs=dict(ORB)
    if a.minor: orbs.update({n:2 for n in ANGLES if n not in ORB})
    if a.orbs:
        custom=json.loads(a.orbs)
        if not isinstance(custom,dict) or any(k not in ANGLES or not isinstance(v,(int,float)) or not 0<=v<=30 for k,v in custom.items()): raise ValueError('orbs must map known aspect names to degrees 0..30')
        orbs.update(custom)
    other=None
    if a.sub=='synastry':
        other=resolve_birth(SimpleNamespace(person=a.other,date=a.other_date,time=a.other_time,place=a.other_place,time_range=a.other_time_range,lat=a.other_lat,lon=a.other_lon,tz=a.other_tz,gender=None))
    results=[]
    for candidate in sample_candidates(b,15):
        birth_jd=jd(candidate['dt'],b['tz']); natal=chart(birth_jd,b['lat'],b['lon'],a.house_system,orbs)
        r={'candidate':candidate,'natal':natal}
        if a.sub=='check':
            x=positions_swe(birth_jd); y=positions_alt(birth_jd); diffs={n:abs(delta(x[n]-v))*60 for n,v in y.items()}
            r.update(swe=x,astronomy_engine=y,diff_arcmin=diffs,max_diff_arcmin=max(diffs.values()))
        elif a.sub in ('transits','progressions'):
            target=jd(datetime.fromisoformat(a.at.replace('Z','+00:00')),b['tz'])
            calc=target if a.sub=='transits' else birth_jd+(target-birth_jd)/365.2425
            c=chart(calc,b['lat'],b['lon'],a.house_system,orbs)
            r.update(chart=c,at=a.at,inter_aspects=aspects(c['planets'],{n:dict(p,speed=0) for n,p in natal['planets'].items()},orbs))
            if a.sub=='progressions': r['progression_rule']='secondary: one ephemeris day per 365.2425 elapsed days; progressed angles at symbolic date'
        elif a.sub=='solar-return':
            start=swe.julday(a.year,1,1,0); ret=swe.solcross_ut(natal['planets']['Sun']['lon'],start,FLAGS)
            r.update(return_chart=chart(ret,(return_geo or b)['lat'],(return_geo or b)['lon'],a.house_system,orbs),year=a.year,return_location=return_geo or {'lat':b['lat'],'lon':b['lon'],'place':b['place']})
        elif other:
            r['other_branches']=[{'candidate':oc,'chart':(c:=chart(jd(oc['dt'],other['tz']),other['lat'],other['lon'],a.house_system,orbs)),'inter_aspects':aspects(natal['planets'],c['planets'],orbs)} for oc in sample_candidates(other,15)]
            r['other_invariants']=invariants([summary(x['chart']) for x in r['other_branches']])
        if 'chart' in r: r['derived_summary']=summary(r['chart'])
        if 'return_chart' in r: r['derived_summary']=summary(r['return_chart'])
        results.append(r)
    out={'engine':natal['engine'],'warnings':list(dict.fromkeys(w for r in results for w in r['natal']['warnings'])),'input':b,'branches':results,'invariants':invariants([summary(r['natal']) for r in results])}
    if b['时间精度']['类型']=='unknown': out['warnings'].append('Unknown birth time: noon is a placeholder; houses/angles are not reliable.')
    if b.get('range_dt'): out['warnings'].append('15-minute samples plus endpoints; invariants describe samples, not a proof over the continuous interval.')
    if any('derived_summary' in r for r in results):
        out['derived_invariants']=invariants([r['derived_summary'] for r in results])
    if other: out['other_input']=other
    if a.save_cache:
        if not b.get('代号'): raise ValueError('--save-cache requires --person')
        from core.cache import save
        cache_rules={**natal['engine']['rules'],'input':{k:str(v) for k,v in b.items() if k not in ('candidates','geo')},'at':getattr(a,'at',None),'year':getattr(a,'year',None),'other':str(other),'return_location':return_geo}
        out['cache']=save(b['代号'],'western-'+a.sub,cache_rules,out)
    return out

def register(subparsers):
    p=subparsers.add_parser('western',help='西方占星（热带黄道）'); sp=p.add_subparsers(dest='sub',required=True)
    for name in ('natal','transits','progressions','solar-return','synastry','check'):
        q=sp.add_parser(name); add_birth_args(q)
        q.add_argument('--house-system',choices=list(HOUSES),default='placidus'); q.add_argument('--minor',action='store_true'); q.add_argument('--orbs'); q.add_argument('--save-cache',action='store_true')
        if name in ('transits','progressions'): q.add_argument('--at',required=True)
        if name=='solar-return': q.add_argument('--year',type=int,required=True)
        if name=='synastry':
            for k in ('other','other-date','other-time','other-time-range','other-place','other-tz'): q.add_argument('--'+k)
            for k in ('other-lat','other-lon'): q.add_argument('--'+k,type=float)
        q.set_defaults(func=run)
