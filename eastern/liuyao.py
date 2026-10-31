"""六爻纳甲：铜钱、年月日时和手工爻值。"""
from __future__ import annotations
import random
from core.draws import draw_once
from . import _iching as ic
from ._cf.liuyao_cast import dress_chart, xun_kong, EIGHT_PALACES

ENGINE = ic.engine('eastern.liuyao', najia='京房八宫', lines='bottom-to-top',
                   coins='heads=3 tails=2; three coins per line', day_boundary='midnight',
                   month='actual solar term UTC+08', changed_relatives='main palace')


def chart(lines, dt):
    lines = list(lines)
    if len(lines) != 6 or any(v not in (6, 7, 8, 9) for v in lines):
        raise ValueError('需要六个爻值，限 6/7/8/9，自下而上')
    lunar, term = ic.lunar_at(dt), ic.lunar_at(dt, True)
    args = (lunar.getDayGan(), lunar.getDayZhi(), term.getMonthZhiExact())
    main = dress_chart(lines, *args)
    pure_num = EIGHT_PALACES[main['palace']][0][0]
    pure = next((u, l) for n, _, u, l in ic.KING_WEN_ORDER if n == pure_num)
    pure_lines = [7 if (bits >> (2-i)) & 1 else 8 for bits in (pure[1], pure[0]) for i in range(3)]
    hidden = dress_chart(pure_lines, *args)
    present = {r['liu_qin'] for r in main['lines']}
    fushen = [r for r in hidden['lines'] if r['liu_qin'] not in present]
    moving = ic.active_lines(lines)
    return {'engine': ENGINE, 'warnings': [], 'datetime': dt.isoformat(), 'raw_lines': lines,
            'main_chart': main,
            'changed_chart': dress_chart(ic.changed_lines(lines), *args, liu_qin_palace=main['palace']) if moving else None,
            'nuclear_chart': dress_chart(ic.nuclear_lines(lines), *args),
            'main_hex': ic.hex_info(lines), 'changed_hex': ic.hex_info(ic.changed_lines(lines)),
            'nuclear_hex': ic.hex_info(ic.nuclear_lines(lines)), 'active_lines': moving,
            '伏神': fushen, '月建': args[2], '日辰': lunar.getDayInGanZhi(), '旬空': xun_kong(*args[:2])}


def run(a):
    b, _ = ic.event_candidates(a)
    rec = None
    if a.method == 'coins':
        rec = draw_once('liuyao-coins', a.question, a.seed,
                        lambda seed: ic.cast_coins(random.Random(seed)), tz=b['tz'],
                        extra={'requested_datetime': str(getattr(a, 'datetime', None) or a.time)}, no_record=a.no_record)
    def compute(dt):
        if rec:
            lines = rec['result']
        elif a.method == 'manual':
            lines = [int(x) for x in a.lines]
        else:
            nums = ic.time_numbers(dt, leap_policy=a.leap_month_policy)
            lines = ic.from_numbers(nums['upper_num'], nums['lower_num'], nums['change_num'])
        out = chart(lines, dt)
        out.update(method=a.method, question=a.question)
        if rec:
            out['draw'] = rec
            out['seed'] = rec['seed']
            if rec.get('redraw_warning'): out['warnings'].append(rec['redraw_warning'])
        return out
    return ic.branch(a, compute)


def register(subparsers):
    p = subparsers.add_parser('liuyao', help='六爻纳甲')
    sp = p.add_subparsers(dest='method', required=True)
    for name in ('coins', 'time', 'manual'):
        q = ic.add_event_args(sp.add_parser(name))
        q.add_argument('--question', default='')
        q.add_argument('--leap-month-policy', choices=['repeat', 'next'])
        if name == 'coins':
            q.add_argument('--seed', type=int)
            q.add_argument('--no-record', action='store_true')
        if name == 'manual': q.add_argument('--lines', required=True)
        q.set_defaults(func=run)
