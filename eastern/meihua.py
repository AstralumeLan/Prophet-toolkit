"""梅花易数：古法农历年月日时、两数及可复现随机起卦。"""
from __future__ import annotations
import random
from core.draws import draw_once
from . import _iching as ic
from ._cf.meihua_cast import ti_yong, ti_yong_relation
from ._cf.utils import XIANTIAN_NUM_TO_TRIGRAM, BAGUA

ENGINE = ic.engine('eastern.meihua', time='农历年支序数+月+日；加时支序数',
                   numbers='A上卦 B下卦 (A+B)动爻', body='静卦为体，动卦为用', day_boundary='midnight')


def from_counts(year, month, day, hour):
    total = year + month + day
    return package(total, total + hour, (total + hour) % 6 or 6,
                   {'year_number': year, 'month_number': month, 'day_number': day, 'hour_number': hour})


def package(upper, lower, change=None, operands=None):
    change = change or ((upper + lower) % 6 or 6)
    lines = ic.from_numbers(upper, lower, change)
    up, low = XIANTIAN_NUM_TO_TRIGRAM[(upper-1)%8+1], XIANTIAN_NUM_TO_TRIGRAM[(lower-1)%8+1]
    body, use = ti_yong(up, low, change)
    return {'engine': ENGINE, 'warnings': [], 'upper_trigram': up, 'lower_trigram': low,
            'changing_line': change, 'main_hex': ic.hex_info(lines),
            'changed_hex': ic.hex_info(ic.changed_lines(lines)), 'nuclear_hex': ic.hex_info(ic.nuclear_lines(lines)),
            'raw_lines': lines, 'operands': operands or {'A': upper, 'B': lower},
            'ti_yong': {'body_trigram': body, 'use_trigram': use,
                       'body_wuxing': BAGUA[body]['wuxing'], 'use_wuxing': BAGUA[use]['wuxing'],
                       'relation': ti_yong_relation(body, use)}}


def run(a):
    b, _ = ic.event_candidates(a)
    rec = None
    if a.method in ('coins', 'random'):
        def draw(seed):
            rng = random.Random(seed)
            return [rng.randint(1, 8), rng.randint(1, 8), rng.randint(1, 6)]
        rec = draw_once('meihua-random', a.question, a.seed, draw, tz=b['tz'], no_record=a.no_record)
    def compute(dt):
        if rec: out = package(*rec['result'])
        elif a.method == 'numbers': out = package(a.A, a.B)
        else:
            n = ic.time_numbers(dt, leap_policy=a.leap_month_policy)
            out = package(n['upper_num'], n['lower_num'], n['change_num'], n)
        out.update(method=a.method, question=a.question, datetime=dt.isoformat())
        if rec:
            out.update(draw=rec, seed=rec['seed'])
            if rec.get('redraw_warning'): out['warnings'].append(rec['redraw_warning'])
        return out
    return ic.branch(a, compute)


def register(subparsers):
    p = subparsers.add_parser('meihua', help='梅花易数')
    sp = p.add_subparsers(dest='method', required=True)
    for name in ('time', 'numbers', 'coins', 'random'):
        q = ic.add_event_args(sp.add_parser(name))
        q.add_argument('--question', default='')
        q.add_argument('--leap-month-policy', choices=['repeat', 'next'])
        if name == 'numbers':
            q.add_argument('A', type=int); q.add_argument('B', type=int)
        if name in ('coins', 'random'):
            q.add_argument('--seed', type=int); q.add_argument('--no-record', action='store_true')
        q.set_defaults(func=run)
