"""Shared event-time handling and I Ching tables (offline)."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from core.inputs import add_birth_args, resolve_birth, shichen_candidates, invariants
from ._cf.yijing_cast import (from_numbers, cast_coins, changed_lines, nuclear_lines,
                              lines_to_trigrams, hex_lookup_by_trigrams, active_lines, KING_WEN_ORDER)
from ._cf.utils import BINARY_TO_TRIGRAM
from ._cf.classical_time_numbers import time_numbers


def engine(name, **rules):
    return {"name": name, "version": "1.0.0", "rules": rules}


def add_event_args(p):
    add_birth_args(p)
    p.add_argument('--datetime', help='ISO 日期时间；有偏移量时转换到 --tz')
    return p


def event_candidates(a, true_solar=False):
    """Birth/range input uses core resolver; event-only input needs no location."""
    tz = getattr(a, 'tz', None) or 'Asia/Shanghai'
    has_location = getattr(a, 'place', None) or (getattr(a, 'lat', None) is not None and getattr(a, 'lon', None) is not None)
    if getattr(a, 'person', None) or getattr(a, 'time_range', None) or (has_location and getattr(a, 'date', None)):
        b = resolve_birth(a)
        return b, [{**c, 'dt': c['dt'].replace(tzinfo=ZoneInfo(b['tz']))}
                   for c in shichen_candidates(b, true_solar=true_solar)]
    value = getattr(a, 'datetime', None)
    clock = getattr(a, 'time', None)
    if value is None and clock and ('T' in clock or ' ' in clock):
        value = clock
    if value:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        dt = dt.replace(tzinfo=ZoneInfo(tz)) if dt.tzinfo is None else dt.astimezone(ZoneInfo(tz))
    else:
        now = datetime.now(ZoneInfo(tz))
        date = getattr(a, 'date', None) or now.date().isoformat()
        clock = clock or now.strftime('%H:%M:%S')
        dt = datetime.fromisoformat(date+'T'+clock).replace(tzinfo=ZoneInfo(tz))
    return {'date': dt.date().isoformat(), 'time': dt.time().isoformat(), 'tz': tz,
            'person': None, 'time_standard': 'clock',
            'raw_datetime_input': value, 'raw_date_input': getattr(a, 'date', None),
            'raw_clock_input': getattr(a, 'time', None)}, [{'label': '起卦时刻', 'dt': dt, 'kind': 'exact'}]


def branch(a, compute, true_solar=False):
    b, candidates = event_candidates(a, true_solar=true_solar)
    results = [compute(c['dt']) for c in candidates]
    if b.get('range_dt'):
        return {'input': b, 'branches': [{'candidate': c, 'chart': r} for c, r in zip(candidates, results)],
                'invariants': invariants(results), 'engine': results[0]['engine'],
                'warnings': ['区间内各时辰分别计算；候选时刻不是确认出生时间。']}
    return {**results[0], 'input': b}


def lunar_at(dt, calendar_instant=False):
    from lunar_python import Solar
    if calendar_instant:
        dt = dt.astimezone(timezone(timedelta(hours=8)))
    return Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second).getLunar()


def hex_info(lines):
    upper, lower = lines_to_trigrams(lines)
    n, name = hex_lookup_by_trigrams(upper, lower)
    return {'number': n, 'name': name, 'upper_trigram': BINARY_TO_TRIGRAM[upper],
            'lower_trigram': BINARY_TO_TRIGRAM[lower], 'raw_lines': lines}
