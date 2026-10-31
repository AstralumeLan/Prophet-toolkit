"""Continuous 置闰 calendar; independently implemented from the stated classical rules.

Sources: 《奇门遁甲统宗·置闰法》、张志春《神奇之门》.
No per-year resets or special-case reference-date overrides. Calendar day offsets
are integral UTC+08 dates, not rounded durations or inclusive day counts.
"""
from bisect import bisect_right
from datetime import date, datetime, timedelta
from functools import lru_cache
from lunar_python import Solar
from ._cf.qimen_dingju import CALENDAR_ZONE
from ._cf.qimen_tables import YANG_JIE_QI, YIN_JIE_QI

TERMS = tuple(YANG_JIE_QI) + tuple(YIN_JIE_QI)
ANCHOR = date(1898, 11, 27)  # 甲午，大雪上元；周新春易学网置闰例。
DISPUTE = ('1995-12-14己卯至冬至12-22日差8日，默认>9不闰（刘金喜/郭志诚/张志春）；'
           '刘广斌《奇门预测学》在此置闰；《奇门遁甲统宗·置闰法》康熙五十七年例'
           '也以8日差（首尾计9日）置闰，--zhirun-threshold 7 可复现该门槛。')


@lru_cache(maxsize=203)
def term_instants(year):
    table = Solar.fromYmdHms(year, 7, 1, 12, 0, 0).getLunar().getJieQiTable()
    result = []
    for name in TERMS:
        s = table['DONG_ZHI' if name == '冬至' else name]
        result.append((datetime(s.getYear(), s.getMonth(), s.getDay(), s.getHour(),
                                s.getMinute(), s.getSecond(), tzinfo=CALENDAR_ZONE), name))
    return tuple(sorted(result))


@lru_cache(maxsize=15)
def timeline(threshold=9):
    if isinstance(threshold, bool) or not isinstance(threshold, int) or not 0 <= threshold <= 14:
        raise ValueError('zhirun-threshold 须为 0..14 的整数（日差严格大于此值才置闰）')
    start = ANCHOR
    rows = []
    for year in range(1898, 2102):
        terms = dict((name, instant) for instant, name in term_instants(year))
        for instant, name in term_instants(year):
            if instant.date() < ANCHOR:
                continue
            lead = (instant.date() - start).days
            # Without intercalation, the following 至 starts on this next 符头.
            if name in ('芒种', '大雪'):
                solstice = terms['夏至' if name == '芒种' else '冬至']
                lead = (solstice.date() - (start + timedelta(days=15))).days
            leap = name in ('芒种', '大雪') and lead > threshold
            rows.append((start, name, False, instant, lead))
            start += timedelta(days=15)
            if leap:
                rows.append((start, name, True, instant, lead))
                start += timedelta(days=15)
    return tuple(rows)


def context(dt, threshold=9):
    # Same local clock-day convention as the existing plate, including optional
    # true-solar correction; term dates and instants remain UTC+08 ephemeris data.
    day = dt.date()
    if not 1898 <= day.year <= 2100:
        raise ValueError('置闰法支持 1898-11-27 至 2100 年')
    if day < ANCHOR:
        raise ValueError('置闰法支持 1898-11-27 至 2100 年')
    rows = timeline(threshold)
    index = bisect_right([r[0] for r in rows], day) - 1
    start, name, leap, instant, trigger_lead = rows[index]
    offset = (day - start).days
    yuan_index = offset // 5
    lead = (instant.date() - start).days
    status = '超神' if lead > 0 else '接气' if lead < 0 else '正授'
    table = YANG_JIE_QI if name in YANG_JIE_QI else YIN_JIE_QI
    # Existing status/day_count/signed_lead_days describe this 节's offset.
    # The 至-based decision lead is separate, including on the repeated 节.
    solstice_lead = trigger_lead if name in ('芒种', '大雪') else None
    if name in ('夏至', '冬至'):
        solstice_lead = rows[index - 1][4]
    return {
        'solstice_lead_days': solstice_lead, 'term_offset_days': lead,
        'jieqi_used': ('闰' if leap else '') + name,
        'base_jieqi': name, 'is_leap': leap,
        'san_yuan': ('上元', '中元', '下元')[yuan_index],
        'ju_type': '阳遁' if name in YANG_JIE_QI else '阴遁',
        'ju_number': table[name][yuan_index],
        'status': status, 'day_count': abs(lead), 'signed_lead_days': lead,
        'upper_yuan_start': start.isoformat(),
        'yuan_start': (start + timedelta(days=yuan_index * 5)).isoformat(),
        'day_in_yuan': offset % 5 + 1,
        'term_instant': instant.isoformat(),
        'trigger_lead_days': (instant.date() - (start - timedelta(days=15) if leap else start)).days,
    }


def rules(threshold):
    return {'zhirun_threshold': threshold, 'comparison': 'calendar_date_difference > threshold',
            'lead_measure': 'UTC+08 至日期 - 不置闰时至上元符头日期',
            'status_measure': '节日期 - 当前上元符头日期；正为超神，负为接气，零为正授；day_count为绝对值',
            'solstice_lead_scope': '芒种/大雪及其闰元和随后至；其他节气为null',
            'anchor': ANCHOR.isoformat() + ' 甲午 大雪上元',
            'intercalation_terms': ['芒种', '大雪'], 'repeat_days': 15,
            'day_boundary': 'effective local midnight', 'term_calendar': 'UTC+08',
            'threshold_dispute': DISPUTE}
