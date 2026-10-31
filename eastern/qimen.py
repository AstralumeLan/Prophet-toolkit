"""时家奇门：符头拆补定局与 rotating-compat 全盘。"""
from __future__ import annotations
from datetime import datetime
from core.solartime import true_solar
from . import _iching as ic
from ._cf import qimen_cast as cf
from ._cf.qimen_dingju import determine_ju, seasonal_context, futou, zhi_shi_position
from ._cf.utils import xun_kong

ENGINE = ic.engine('eastern.qimen', plate='rotating-compat', ju_method='拆补：符头三元+实交节',
                   center='环盘中五寄坤二；天禽保留中五', calendar='solar terms at actual UTC+08 instant',
                   day_boundary='midnight', horse='hour branch 三合驿马')


def chart(dt, lon=None, ju_method="chaibu", zhirun_threshold=9):
    if ju_method not in ("chaibu", "拆补", "futou", "zhirun", "置闰"):
        raise ValueError("未知定局法")
    use_zhirun = ju_method in ("zhirun", "置闰")
    original = dt
    correction = None
    if lon is not None:
        if not -180 <= lon <= 180: raise ValueError('经度须为 -180..180')
        correction = true_solar(dt.replace(tzinfo=None), lon, str(dt.tzinfo))
        dt = datetime.fromisoformat(correction['真太阳时']).replace(tzinfo=dt.tzinfo)
    lunar = ic.lunar_at(dt)
    term = seasonal_context(original)
    ju_type, yuan, ju = determine_ju(term['name'], lunar.getDayInGanZhi())
    extension = {}
    engine = ENGINE
    if use_zhirun:
        from . import _qimen_zhirun as zr
        detail = zr.context(dt, zhirun_threshold)
        ju_type, yuan, ju = detail['ju_type'], detail['san_yuan'], detail['ju_number']
        engine = {**ENGINE, 'rules': {**ENGINE['rules'], 'ju_method': '置闰',
                                     'zhirun_threshold': zhirun_threshold}}
        extension = {'jieqi_used': detail['jieqi_used'], 'zhirun_context': detail,
                     'rules_ext': zr.rules(zhirun_threshold)}
    earth = cf.earth_plate(ju_type, ju)
    hg = lunar.getTimeInGanZhi()
    head, yi = cf.xun_head(*hg)
    effective = yi if hg[0] == '甲' else hg[0]
    origin = next(p for p, g in earth.items() if g == yi)
    target = next(p for p, g in earth.items() if g == effective)
    seq = cf.YANG_PALACE_SEQ if ju_type == '阳遁' else cf.YIN_PALACE_SEQ
    shift = (seq.index(target) - seq.index(origin)) % 9
    heaven = {seq[(k+shift)%9]: earth[p] for k, p in enumerate(seq)}
    stars = cf.star_plate(origin, target, ju_type)
    raw_door, door_palace = zhi_shi_position(origin, hg, ju_type)
    doors = cf.men_plate(origin, door_palace, ju_type)
    gods = cf.shen_plate(target, ju_type)
    horse = next(h for group, h in [('申子辰','寅'), ('寅午戌','申'), ('亥卯未','巳'), ('巳酉丑','亥')] if hg[1] in group)
    return {**extension, 'ju_method': 'zhirun' if use_zhirun else 'chaibu', 'engine': engine, 'warnings': ['rotating-compat 为参考实现兼容盘；天禽寄宫等流派差异未作古籍全盘校核。'],
            'datetime': original.isoformat(), 'effective_datetime': dt.isoformat(), 'solar_time': correction,
            'ganzhi': {'year': lunar.getYearInGanZhi(), 'month': lunar.getMonthInGanZhi(),
                       'day': lunar.getDayInGanZhi(), 'hour': hg},
            'jieqi': term['name'], 'term_context': term, 'ju_type': ju_type, 'ju_number': ju,
            'san_yuan': yuan, 'futou': futou(lunar.getDayInGanZhi())[0], 'xun_head': head, 'xun_yi': yi,
            'zhi_fu_star': stars[cf._resolve_ring_palace(target)], 'zhi_fu_palace': target,
            'zhi_fu_origin_palace': origin, 'zhi_shi_men': doors[cf._resolve_ring_palace(door_palace)],
            'zhi_shi_palace': door_palace, 'zhi_shi_raw_palace': raw_door,
            '空亡': xun_kong(*hg), '马星': horse,
            'palaces': cf.build_palaces(earth, heaven, doors, stars, gods)}


def run(a):
    return ic.branch(a, lambda dt: chart(dt, a.lon, a.ju_method, a.zhirun_threshold), true_solar=a.lon is not None)


def register(subparsers):
    p = subparsers.add_parser('qimen', help='时家奇门转盘')
    sp = p.add_subparsers(dest='method', required=True)
    q = ic.add_event_args(sp.add_parser('chart'))
    q.add_argument('--ju-method', choices=['chaibu', '拆补', 'futou', 'zhirun', '置闰'], default='chaibu',
                   help='默认符头拆补；zhirun/置闰为连续超神接气置闰法')
    q.add_argument('--zhirun-threshold', type=int, default=9,
                   help='至日期减不闰时至上元符头日期，严格大于门槛才闰（0..14；默认9；7复现8日差置闰）')
    q.set_defaults(func=run)
