"""Independent classical placement; no iztro output or code executed here.

Branch indices start at 子. Rules follow 紫微斗数全书安星诀: 寅起正月，
逆生时安命、顺生时安身；五虎遁、纳音定局；补日整除，偶进奇退。
Compatibility choices: iztro split leap months (days 1–15 same month,
16+ next month), except late 子 retains the original month index. Late 子
advances the lunar day, wrapping at month end, but uses the original solar
calendar date's month/year for palace placement, as iztro 2.6.1 does.
"""
from lunar_python import Solar
from lunar_python.util import LunarUtil

BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
STEMS = '甲乙丙丁戊己庚辛壬癸'
ZI = dict(zip(['紫微','天机','太阳','武曲','天同','廉贞'], [0,-1,-3,-4,-5,-8]))
FU = dict(zip(['天府','太阴','贪狼','巨门','天相','天梁','七杀','破军'], [0,1,2,3,4,5,6,10]))
TRANSFORMS = [
    ['廉贞','破军','武曲','太阳'], ['天机','天梁','紫微','太阴'],
    ['天同','天机','文昌','廉贞'], ['太阴','天同','天机','巨门'],
    ['贪狼','太阴','右弼','天机'], ['武曲','贪狼','天梁','文曲'],
    ['太阳','武曲','太阴','天同'], ['巨门','太阳','文曲','文昌'],
    ['天梁','紫微','左辅','武曲'], ['破军','巨门','太阴','贪狼']]
RULES = {'leap_month':'split: 1–15 same month; 16+ next month; late zi original month',
         'late_zi':'advance day only (wrap month length); palace month/year from original date',
         'year':'lunar new year', 'geng_sihua':'太阳禄 武曲权 太阴科 天同忌 (iztro variant; 庚年四化存在流派差异)',
         'scope':'14 major stars, 昌曲辅弼, 命身宫, 命宫干支纳音局, 生年四化'}


def calculate(dt):
    lunar = Solar.fromYmd(dt.year, dt.month, dt.day).getLunar()
    hour = ((dt.hour+1)//2) % 12
    late = dt.hour == 23
    month = abs(lunar.getMonth())
    effective_month = month + int(lunar.getMonth() < 0 and lunar.getDay() > 15 and not late)
    soul_index = (effective_month-1-hour) % 12  # 寅=0
    soul = (soul_index+2) % 12
    body = (effective_month+1+hour) % 12
    year_stem = STEMS.index(lunar.getYearGan())
    stem = STEMS[((year_stem % 5)*2+2+soul_index) % 10]
    ganzhi = stem+BRANCHES[soul]
    nayin = LunarUtil.NAYIN[ganzhi]
    element = nayin[-1]
    bureau = {'水':2,'木':3,'金':4,'土':5,'火':6}[element]
    day = lunar.getDay()
    if late:
        from datetime import timedelta
        nxt = dt+timedelta(days=1)
        day = Solar.fromYmd(nxt.year,nxt.month,nxt.day).getLunar().getDay()
    padding = (-day) % bureau
    zi = (2+(day+padding)//bureau-1+(padding if padding%2 == 0 else -padding)) % 12
    fu = (4-zi) % 12
    positions = {s:BRANCHES[(zi+o)%12] for s,o in ZI.items()}
    positions.update({s:BRANCHES[(fu+o)%12] for s,o in FU.items()})
    positions.update({'文昌':BRANCHES[(10-hour)%12], '文曲':BRANCHES[(4+hour)%12],
                      '左辅':BRANCHES[(4+effective_month-1)%12], '右弼':BRANCHES[(10-effective_month+1)%12]})
    return {'engine':{'name':'validate.ziwei_indep','version':'1.0.0','rules':RULES},'warnings':[],
            'positions':positions,'soul':BRANCHES[soul],'body':BRANCHES[body], 'soul_ganzhi':ganzhi,
            'nayin':nayin,'bureau':f'{element}{"零一二三四五六"[bureau]}局',
            'sihua':dict(zip('禄权科忌',TRANSFORMS[year_stem]))}
