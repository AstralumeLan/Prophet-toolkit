"""Offline Lahiri Jyotish. All sign indices are zero based (Aries=0)."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from core.inputs import add_birth_args, resolve_birth, sample_candidates, invariants
from vedic._tables import (ZODIAC_SIGNS as SIGNS, SIGN_LORDS, NAKSHATRAS,
                           VIMSHOTTARI_YEARS as YEARS, DASHA_SEQUENCE as SEQUENCE,
                           EXALTATION, OWN_SIGNS, NATURAL_FRIENDS, NATURAL_ENEMIES,
                           BAV_DASHAFLOW)

VERSION = '1.0.0'
YEAR_DAYS = 365.25
PLANETS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
           'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
           'Venus': swe.VENUS, 'Saturn': swe.SATURN}
# Half-open intervals; Mercury's overlapping exaltation is resolved in favour
# of moolatrikona. Natural (permanent) friendship only, no compound friendship.
MOOLA = {'Sun': (4, 0, 20), 'Moon': (1, 3, 30), 'Mars': (0, 0, 12),
         'Mercury': (5, 15, 20), 'Jupiter': (8, 0, 10),
         'Venus': (6, 0, 15), 'Saturn': (10, 0, 20)}
BAV_PARASHARA = deepcopy(BAV_DASHAFLOW)
BAV_PARASHARA['Moon']['Moon'] = [1, 3, 6, 7, 9, 10, 11]
BAV_PARASHARA['Moon']['Mars'] = [2, 3, 5, 6, 10, 11]
BAV_PARASHARA['Venus']['Mars'] = [3, 4, 6, 9, 11, 12]
BAV_PVR = deepcopy(BAV_PARASHARA)
BAV_PVR['Moon']['Jupiter'] = [1, 2, 4, 7, 8, 10, 11]
BAV_SOURCE = ("P.V.R. Narasimha Rao, Vedic Astrology: An Integrated Approach, "
              "Ashtakavarga chapter, Controversies; implemented from PVR's published "
              "description; not verified against PyJHora")
NODE_SOURCES = {
    'none': 'Unassigned; schools disagree.',
    'bphs': 'BPHS ch.3, planetary characteristics, commonly translated by R. Santhanam; node sign dignities vary across editions.',
    'gemini-sagittarius': 'Later-text / South-Indian Gemini–Sagittarius exaltation convention; own Virgo/Pisces variant noted but not assigned here.'}


def selected_engine(node, bav_table, node_dignity='none'):
    result = engine(node, bav_table)
    if node_dignity != 'none':
        result['rules']['node_dignity'] = node_dignity
    return result


def engine(node='mean', bav_table='parashara'):
    return {'name': 'vedic.jyotish', 'version': VERSION, 'rules': {
        'zodiac': 'sidereal', 'ayanamsa': 'Lahiri (Swiss SIDM_LAHIRI)',
        'ephemeris': 'Swiss Ephemeris Moshier', 'swisseph_version': swe.version,
        'houses': 'whole-sign from sidereal Lagna', 'node': node,
        'vargas': 'Parashara D1/D7/D9/D10/D12; forward counting',
        'dasha': 'Vimshottari; full pre-birth maha start; half-open periods',
        'dasha_year_days': YEAR_DAYS, 'dasha_dates': 'UTC ISO timestamps; --at date is local midnight',
        'bav_table': bav_table, 'bav_reduction': 'none; SAV excludes Lagna BAV',
        'bav_default_note': 'Parashara BPHS profile; pyjhora-pvr is not claimed or imported',
        'dignity': 'natural friendship; moolatrikona overrides exaltation; nodes unassigned',
        'moolatrikona_intervals': MOOLA, 'approx_sampling_minutes': 15,
        'birth_time': 'original clock time converted via IANA timezone; no solar-time substitution'}}


def nakshatra(longitude):
    x = longitude % 360 * 3 / 40
    i = int(x)
    return {'index': i + 1, **NAKSHATRAS[i], 'pada': min(4, int((x-i)*4)+1),
            'degree_in_nakshatra': (x-i)*40/3}


def varga(longitude, division):
    """Return Parashari divisional sign index; interval boundaries are half-open."""
    longitude %= 360
    s, degree = int(longitude / 30), longitude % 30
    part = min(division - 1, int(degree * division / 30))
    if division == 1:
        return s
    if division == 9:
        return int(longitude * 9 / 30) % 12
    if division == 7:
        return (s + (6 if s % 2 else 0) + part) % 12
    if division == 10:
        return (s + (8 if s % 2 else 0) + part) % 12
    if division == 12:
        return (s + part) % 12
    raise ValueError('supported vargas: 1, 7, 9, 10, 12')


def dignity(planet, longitude, node_dignity='none'):
    if node_dignity not in NODE_SOURCES:
        raise ValueError('unknown node dignity convention')
    if planet in ('Rahu', 'Ketu') and node_dignity != 'none':
        sign = int(longitude % 360 // 30)
        exalt = (1 if planet == 'Rahu' else 7) if node_dignity == 'bphs' else (2 if planet == 'Rahu' else 8)
        if sign == exalt:
            return 'exalted'
        if sign == (exalt+6) % 12:
            return 'debilitated'
        if node_dignity == 'bphs':
            if sign == (2 if planet == 'Rahu' else 8):
                return 'moolatrikona'
            if sign == (10 if planet == 'Rahu' else 7):
                return 'own'
        return 'unassigned'
    if planet not in PLANETS:
        return 'unassigned'
    s, degree = int(longitude % 360 / 30), longitude % 30
    mt, lo, hi = MOOLA[planet]
    if s == mt and lo <= degree < hi:
        return 'moolatrikona'
    exalted = SIGNS.index(EXALTATION[planet][0])
    if s == exalted:
        return 'exalted'
    if s == (exalted + 6) % 12:
        return 'debilitated'
    if SIGNS[s] in OWN_SIGNS[planet]:
        return 'own'
    lord = SIGN_LORDS[SIGNS[s]]
    return ('friend' if lord in NATURAL_FRIENDS[planet] else
            'enemy' if lord in NATURAL_ENEMIES[planet] else 'neutral')


def ashtakavarga(positions, lagna, profile='parashara'):
    if profile not in ('parashara', 'dashaflow', 'varahamihira', 'pyjhora-pvr'):
        raise ValueError('unknown BAV profile')
    table = BAV_PARASHARA if profile == 'parashara' else BAV_PVR if profile == 'pyjhora-pvr' else BAV_DASHAFLOW
    sources = {**positions, 'Ascendant': lagna}
    bav, scatter = {}, {}
    for target, contributors in table.items():
        row = [0] * 12
        scatter[target] = {}
        for source, houses in contributors.items():
            marks = [0] * 12
            for h in houses:
                k = (sources[source] + h - 1) % 12
                row[k] += 1
                marks[k] = 1
            scatter[target][source] = marks
        bav[target] = row
    sav = [sum(row[i] for row in bav.values()) for i in range(12)]
    return {'profile': profile, 'sign_order': SIGNS, 'BAV': bav, 'SAV': sav,
            'planet_totals': {p: sum(r) for p, r in bav.items()},
            'grand_total': sum(sav), 'reduced': False, 'contributions': scatter,
            'bav_profile_source': BAV_SOURCE if profile == 'pyjhora-pvr' else
                'dashaflow MIT table / Varahamihira' if profile in ('dashaflow', 'varahamihira') else
                'Legacy parashara profile; Phaladeepika ch.23 variant footnote',
            'notes': ['Legacy parashara applies PVR conflicts (1) and (3), but Moon/Jupiter retains 12 instead of 2; differs from PVR reading of Parasara.'] if profile == 'parashara' else []}


def vimshottari(moon_longitude, birth, at=None, levels=3):
    """One full 120-year cycle from the pre-birth maha start, plus next maha.

    The extra maha completes coverage through birth+120 years. Child periods
    subdivide the FULL parent, never the truncated balance remaining at birth.
    """
    if levels not in (1, 2, 3):
        raise ValueError('levels must be 1..3')
    if birth.tzinfo is None:
        birth = birth.replace(tzinfo=timezone.utc)
    birth = birth.astimezone(timezone.utc)
    at = at or birth
    if at.tzinfo is None:
        at = at.replace(tzinfo=timezone.utc)
    at = at.astimezone(timezone.utc)
    x = moon_longitude % 360 * 3 / 40
    first = int(x) % 9
    lord = SEQUENCE[first]
    start = birth - timedelta(days=(x-int(x))*YEARS[lord]*YEAR_DAYS)
    cycle_start = start
    current = {}

    def build(start, end, lord, depth):
        active = start <= at < end
        key = ('maha', 'antar', 'pratyantar')[depth-1]
        period = {'lord': lord, 'start': start.isoformat(), 'end': end.isoformat(),
                  'years': (end-start).total_seconds()/86400/YEAR_DAYS}
        if active:
            current[key] = dict(period)
        if depth < levels:
            subs, cursor = [], start
            offset = SEQUENCE.index(lord)
            for j in range(9):
                sublord = SEQUENCE[(offset+j) % 9]
                stop = cursor + (end-start)*(YEARS[sublord]/120)
                if j == 8:
                    stop = end
                subs.append(build(cursor, stop, sublord, depth+1))
                cursor = stop
            period['children'] = subs
        return period

    timeline = []
    for i in range(10):
        lord = SEQUENCE[(first+i) % 9]
        end = start + timedelta(days=YEARS[lord]*YEAR_DAYS)
        timeline.append(build(start, end, lord, 1))
        start = end
    return {'birth_lord': SEQUENCE[first], 'balance_years': (1-(x-int(x)))*YEARS[SEQUENCE[first]],
            'year_days': YEAR_DAYS, 'cycle_years': 120,
            'cycle_start': cycle_start.isoformat(),
            'cycle_end': (cycle_start+timedelta(days=120*YEAR_DAYS)).isoformat(),
            'at': at.isoformat(), 'current': current, 'timeline': timeline,
            'coverage_note': 'full birth maha plus next nine; current empty outside coverage'}


def calculate_chart(local, lat, lon, tz, node='mean', bav_table='parashara', at=None, levels=3, node_dignity='none', shadbala=False):
    if not -90 < lat < 90 or not -180 <= lon <= 180:
        raise ValueError('latitude must be between poles; longitude in [-180,180]')
    if node not in ('mean', 'true'):
        raise ValueError('node must be mean or true')
    utc = local.replace(tzinfo=ZoneInfo(tz)).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute/60 + (utc.second+utc.microsecond/1e6)/3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    # Ascendant is independent of quadrant house division, so Equal houses
    # avoid the Placidus polar failure. Output houses remain whole-sign.
    _, axes = swe.houses_ex(jd, lat, lon, b'E', swe.FLG_SIDEREAL)
    asc = axes[0] % 360
    lagna = int(asc / 30)
    warnings = ['Rahu/Ketu dignity varies by tradition and is left unassigned.'] if node_dignity == 'none' else ['Node dignities use the explicitly selected convention; traditions differ.']
    positions, speeds = {}, {}
    for name, ident in {**PLANETS, 'Rahu': swe.MEAN_NODE if node == 'mean' else swe.TRUE_NODE}.items():
        values, returned = swe.calc_ut(jd, ident, flags)
        if name in PLANETS and not returned & swe.FLG_MOSEPH:
            raise RuntimeError('Moshier ephemeris was not used')
        positions[name], speeds[name] = values[0] % 360, values[3]
    positions['Ketu'], speeds['Ketu'] = (positions['Rahu']+180) % 360, speeds['Rahu']
    grahas = {}
    for p, longitude in positions.items():
        sign = int(longitude / 30)
        grahas[p] = {'longitude': longitude, 'sign': SIGNS[sign], 'sign_index': sign,
                     'degree': longitude % 30, 'house': (sign-lagna) % 12+1,
                     'nakshatra': nakshatra(longitude), 'retrograde': speeds[p] < 0,
                     'speed_deg_per_day': speeds[p], 'dignity': dignity(p, longitude, node_dignity)}
    vargas = {}
    for d in (1, 9, 7, 10, 12):
        a = varga(asc, d)
        vargas[f'D{d}'] = {'lagna': SIGNS[a], 'grahas': {
            p: {'sign': SIGNS[varga(x, d)], 'house': (varga(x, d)-a) % 12+1}
            for p, x in positions.items()}}
    query = datetime.fromisoformat(at).replace(tzinfo=ZoneInfo(tz)) if at else datetime.now(ZoneInfo(tz))
    result = {'engine': selected_engine(node, bav_table, node_dignity), 'warnings': warnings,
            'clock_time': local.isoformat(), 'utc': utc.isoformat(), 'julian_day_ut': jd,
            'ayanamsa': swe.get_ayanamsa_ut(jd),
            'lagna': {'longitude': asc, 'sign': SIGNS[lagna], 'degree': asc % 30,
                      'nakshatra': nakshatra(asc)},
            'grahas': grahas,
            'house_lords': [{'house': i+1, 'sign': SIGNS[(lagna+i) % 12],
                             'lord': SIGN_LORDS[SIGNS[(lagna+i) % 12]]} for i in range(12)],
            'vargas': vargas,
            'dasha': vimshottari(positions['Moon'], utc, query, levels),
            'ashtakavarga': ashtakavarga({p: int(x/30) for p, x in positions.items()}, lagna, bav_table)}

    result['rules_ext'] = {'node_dignity': node_dignity,
                           'node_dignity_source': NODE_SOURCES[node_dignity],
                           'shadbala': bool(shadbala)}
    if shadbala:
        result['shadbala'] = _chart_shadbala(jd, lat, lon, positions, speeds, asc, axes[1])
    return result


def _chart_shadbala(jd, lat, lon, positions, speeds, asc, mc):
    from vedic._shadbala import calculate_shadbala, raman_mean_positions
    # Find preceding sunrise and following sunset, without inventing polar events.
    def event(start, kind):
        status, times = swe.rise_trans(start, swe.SUN,
            kind | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION,
            (lon, lat, 0), flags=swe.FLG_MOSEPH)
        if status != 0:
            raise ValueError('Shadbala requires sunrise/sunset; unavailable at this polar date/location')
        return times[0]
    sunrise = event(jd-1, swe.CALC_RISE)
    if sunrise > jd:
        sunrise = event(jd-2, swe.CALC_RISE)
    sunset = event(sunrise+1e-6, swe.CALC_SET)
    # Convert to local solar calendar day for Raman condensed ahargana.
    y, m, d, _ = swe.revjul(sunrise + lon/360)
    solar_date = datetime(y, m, d)
    ahargana = (solar_date-datetime(1827, 5, 2)).days + 1
    week = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')
    weekday = week[(solar_date.weekday()+1) % 7]
    year_lord = week[(3 + 3*(ahargana//360)) % 7]
    month_lord = week[(3 + 2*(ahargana//30)) % 7]
    # Apparent local solar time = UT + longitude + Swiss equation-of-time.
    apparent_hour = ((jd+.5+lon/360+swe.time_equ(jd)) % 1)*24
    natha = abs(apparent_hour-12)
    means, seeghra = raman_mean_positions(jd)
    return calculate_shadbala(positions, {p: speeds[p] for p in PLANETS}, asc, mc,
        ayanamsa=swe.get_ayanamsa_ut(jd), natha_hours=natha,
        hours_since_sunrise=(jd-sunrise)*24, day_hours=(sunset-sunrise)*24,
        weekday_lord=weekday, year_lord=year_lord, month_lord=month_lord,
        mean_longitudes=means, seeghrochcha=seeghra)


def _conclusions(chart):
    """Discrete conclusions, avoiding exact degrees that always vary over samples."""
    g = chart['grahas']
    return {'lagna_sign': chart['lagna']['sign'], 'house_lords': chart['house_lords'],
            'graha_signs': {p: r['sign'] for p, r in g.items()},
            'graha_houses': {p: r['house'] for p, r in g.items()},
            'graha_dignities': {p: r['dignity'] for p, r in g.items()},
            'moon_nakshatra': g['Moon']['nakshatra']['name'],
            'moon_pada': g['Moon']['nakshatra']['pada'],
            'moon_nakshatra_lord': g['Moon']['nakshatra']['lord'],
            **{f'{d}_lagna': v['lagna'] for d, v in chart['vargas'].items()},
            **{f'{d}_graha_signs': {p: r['sign'] for p, r in v['grahas'].items()}
               for d, v in chart['vargas'].items()},
            'dasha_current_lords': {k: v['lord'] for k, v in chart['dasha']['current'].items()},
            'BAV': chart['ashtakavarga']['BAV'], 'SAV': chart['ashtakavarga']['SAV']}


def run(args):
    birth = resolve_birth(args)
    if args.save_cache and not birth['代号']:
        raise ValueError('--save-cache requires --person')
    if birth['时间精度']['类型'] == 'unknown':
        raise ValueError('Vedic Lagna/dasha requires a time or --time-range; noon placeholder is not used')
    branches, conclusions = [], []
    for candidate in sample_candidates(birth):
        chart = calculate_chart(candidate['dt'], birth['lat'], birth['lon'], birth['tz'],
                                args.node, args.bav_table, args.at, args.levels,
                                args.node_dignity, args.shadbala or args.sub == 'shadbala')
        conclusions.append(_conclusions(chart) | ({'shadbala_strong': {p: r['strong'] for p, r in chart['shadbala']['grahas'].items()}} if 'shadbala' in chart else {}))
        if args.sub == 'nakshatra':
            chart = {k: chart[k] for k in ('engine', 'warnings', 'clock_time', 'utc')} | {
                'moon': chart['grahas']['Moon']['nakshatra'],
                'grahas': {p: r['nakshatra'] for p, r in chart['grahas'].items()}}
        elif args.sub == 'shadbala':
            chart = {k: chart[k] for k in ('engine', 'warnings', 'clock_time', 'utc', 'rules_ext', 'shadbala')}
        elif args.sub == 'dasha':
            chart = {k: chart[k] for k in ('engine', 'warnings', 'clock_time', 'utc', 'dasha')}
        branches.append({'candidate': candidate, 'chart': chart})
    out = {'engine': selected_engine(args.node, args.bav_table, args.node_dignity), 'warnings': [],
           'rules_ext': {'node_dignity': args.node_dignity, 'node_dignity_source': NODE_SOURCES[args.node_dignity], 'shadbala': args.shadbala or args.sub == 'shadbala'},
           'person': birth['代号'], 'input': birth, 'branches': branches}
    if birth.get('range_dt'):
        out['warnings'].append('15-minute samples and endpoints only; invariants apply to samples, not a proof over the continuous interval.')
        out['invariants'] = invariants(conclusions)
    if birth['时间精度']['类型'] == 'provisional':
        out['warnings'].append('Birth time is provisional, not a verified exact record.')
    if args.save_cache:
        from core.cache import save
        # Cache identity must distinguish overrides, command, query date and levels.
        rules = {**out['engine']['rules'], 'command': args.sub, 'at': args.at,
                 'levels': args.levels, 'resolved_input': birth}
        if args.shadbala:
            rules['shadbala'] = True
        # core.cache hashes JSON without default=str: use stable string dates here.
        import json
        rules = json.loads(json.dumps(rules, default=str, ensure_ascii=False))
        out['cache_path'] = save(birth['代号'], f'vedic-{args.sub}', rules, out)
    return out


def register(subparsers):
    parser = subparsers.add_parser('vedic', help='印度占星：Lahiri 恒星黄道')
    subs = parser.add_subparsers(dest='sub', required=True)
    for command in ('chart', 'dasha', 'nakshatra', 'shadbala'):
        p = subs.add_parser(command)
        add_birth_args(p)
        p.add_argument('--node', choices=('mean', 'true'), default='mean')
        p.add_argument('--bav-table', choices=('dashaflow', 'parashara', 'varahamihira', 'pyjhora-pvr'), default='parashara')
        p.add_argument('--node-dignity', choices=tuple(NODE_SOURCES), default='none')
        p.add_argument('--shadbala', action='store_true', help='include Raman sixfold strength')
        p.add_argument('--at', help='查询日期 YYYY-MM-DD（出生地时区午夜）')
        p.add_argument('--levels', type=int, choices=(1, 2, 3), default=3)
        p.add_argument('--save-cache', action='store_true')
        p.set_defaults(func=run)
