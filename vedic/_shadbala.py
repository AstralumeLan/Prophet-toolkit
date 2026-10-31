"""Raman/Sripathi Shadbala, independently transcribed from Graha and Bhava Balas.

All angles are degrees; strengths are virupas (shashtiamsas). Pure calculation
accepts historical intermediate mean longitudes without an ephemeris dependency.
"""
from math import sqrt
from vedic._tables import (ZODIAC_SIGNS, SIGN_LORDS, EXALTATION,
                           NATURAL_FRIENDS, NATURAL_ENEMIES)

PLANETS = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')
NAISARGIKA = dict(zip(PLANETS, (60, 51.43, 17.14, 25.70, 34.28, 42.85, 8.57)))
REQUIRED = dict(zip(PLANETS, (5, 6, 5, 7, 6.5, 5.5, 5)))
LORDS = [SIGN_LORDS[s] for s in ZODIAC_SIGNS]
MOOLA = {'Sun': (4, 0, 20), 'Moon': (1, 3, 30), 'Mars': (0, 0, 12),
         'Mercury': (5, 15, 20), 'Jupiter': (8, 0, 10),
         'Venus': (6, 0, 15), 'Saturn': (10, 0, 20)}
SOURCE = 'B.V. Raman, Graha and Bhava Balas, arts.18–122, 136–139; Sripathi method'


def arc(x):
    return abs((x + 180) % 360 - 180)


def division(x, d):
    """Seven classical vargas, including unequal Parashari trimsamsa."""
    x %= 360
    s, degree = int(x // 30), x % 30
    part = min(d - 1, int(degree * d / 30))
    if d == 1:
        return s
    if d == 2:
        return (4 if degree < 15 else 3) if s % 2 == 0 else (3 if degree < 15 else 4)
    if d == 3:
        return (s + 4 * part) % 12
    if d == 7:
        return (s + (6 if s % 2 else 0) + part) % 12
    if d == 9:
        return int(x * 9 / 30) % 12
    if d == 12:
        return (s + part) % 12
    if d == 30:
        ends, signs = ((5, 10, 18, 25, 30), (0, 10, 8, 2, 6)) if s % 2 == 0 else ((5, 12, 20, 25, 30), (1, 5, 11, 9, 7))
        return next(sign for end, sign in zip(ends, signs) if degree < end)
    raise ValueError('unsupported saptavarga')


def saptavargaja(longitudes, planet):
    natal = {p: int(longitudes[p] % 360 // 30) for p in PLANETS}
    rows = {}
    for d in (1, 2, 3, 7, 9, 12, 30):
        s = division(longitudes[planet], d)
        lord = LORDS[s]
        mt, lo, hi = MOOLA[planet]
        if d == 1 and s == mt and lo <= longitudes[planet] % 30 < hi:
            value = 45
        elif lord == planet:
            value = 30
        else:
            natural = (1 if lord in NATURAL_FRIENDS[planet] else
                       -1 if lord in NATURAL_ENEMIES[planet] else 0)
            temporary = 1 if (natal[lord] - natal[planet]) % 12 in (1, 2, 3, 9, 10, 11) else -1
            value = {-2: 1.875, -1: 3.75, 0: 7.5, 1: 15, 2: 22.5}[natural + temporary]
        rows[f'D{d}'] = {'sign_index': s, 'lord': lord, 'virupas': value}
    return rows


def aspect_value(angle, planet):
    """Raman arts.114–115: ordinary piecewise aspect plus special aspect."""
    a = angle % 360
    if a < 30 or a >= 300:
        v = 0
    elif a < 60:
        v = (a - 30) / 2
    elif a < 90:
        v = a - 45
    elif a < 120:
        v = (120 - a) / 2 + 30
    elif a < 150:
        v = 150 - a
    elif a < 180:
        v = (a - 150) * 2
    else:
        v = (300 - a) / 2
    intervals = {'Mars': ((90, 120), (210, 240), 15),
                 'Jupiter': ((120, 150), (240, 270), 30),
                 'Saturn': ((60, 90), (270, 300), 45)}
    if planet in intervals:
        first, second, extra = intervals[planet]
        if any(lo <= a < hi for lo, hi in (first, second)):
            v += extra
    return v


def kranti(tropical):
    """Raman art.73 six linear 15-degree increments, maximum 24 degrees."""
    x = tropical % 360
    b = arc(x)
    if b > 90:
        b = 180 - b
    increments = (362, 341, 299, 236, 150, 52)
    n = min(5, int(b // 15))
    value = (sum(increments[:n]) + increments[n] * (b - n * 15) / 15) / 60
    return value if x < 180 else -value


def raman_mean_positions(jd_ut):
    """Arts.88–104: linear epoch model, NOT modern osculating mean elements.

    Rates from Tables IV–IX (longest interval columns). The supplied text has
    misprints; use art.101's mean Sun for Saturn's seeghrochcha, not art.104's
    isolated 151.23 typo. Epoch is 1900-01-01 00:00 at 76 E.
    """
    from datetime import datetime, timedelta, timezone
    days = jd_ut - (2415020.5 - 76 / 360)
    dt = datetime(1900, 1, 1, tzinfo=timezone.utc) + timedelta(days=days)
    t = dt.year - 1900
    sun = (257.4568 + .98560265 * days) % 360
    mean = {'Sun': sun, 'Mercury': sun, 'Venus': sun,
            'Mars': (270.22 + .524019 * days) % 360,
            'Jupiter': (220.04 + .083096 * days - (3.33 + .0067*t)) % 360,
            'Saturn': (236.74 + .033439 * days + 5 + .001*t) % 360}
    seeghra = {'Mars': sun, 'Jupiter': sun, 'Saturn': sun,
              'Mercury': (164 + 4.0923345*days + 6.67 - .00133*t) % 360,
              'Venus': (328.51 + 1.602146*days - 5 - .001*t) % 360}
    return mean, seeghra


def calculate_shadbala(longitudes, speeds, lagna, mc, *, ayanamsa,
                       natha_hours, hours_since_sunrise, day_hours,
                       weekday_lord, year_lord, month_lord,
                       mean_longitudes, seeghrochcha, mercury_benefic=None,
                       krantis=None):
    """Pure sixfold calculation; time quantities refer to the preceding sunrise.

    natha_hours is distance from apparent noon, in [0,12]. day_hours is the
    sunrise-to-sunset interval. Weekday uses the Hindu sunrise day; horas are
    fixed 60-minute hours (Raman art.69), not unequal seasonal hours.
    Optional krantis supplies the book's rounded intermediate declinations.
    speeds is retained as auditable input; never substituted for Chesta geometry.
    """
    if not (0 < day_hours < 24 and 0 <= natha_hours <= 12 and 0 <= hours_since_sunrise < 24):
        raise ValueError('invalid Shadbala day/natha/sunrise interval')
    for lord in (weekday_lord, year_lord, month_lord):
        if lord not in PLANETS:
            raise ValueError('time lord must be a classical planet')
    x = {p: longitudes[p] % 360 for p in PLANETS}
    phase = arc(x['Moon'] - x['Sun']) / 3
    # Art.53 Moon is benefic between bright eighth and dark eighth (~90–270).
    moon_benefic = 90 <= (x['Moon'] - x['Sun']) % 360 <= 270
    if mercury_benefic is None:
        # Explicit runtime convention for "badly associated": same sign as a
        # natural malefic or a weak Moon, including solar combustion.
        bad = ['Sun', 'Mars', 'Saturn'] + ([] if moon_benefic else ['Moon'])
        mercury_benefic = not any(int(x['Mercury']//30) == int(x[p]//30) for p in bad)
    benefic = {'Moon': moon_benefic, 'Mercury': mercury_benefic, 'Jupiter': True, 'Venus': True}
    daylight = hours_since_sunrise < day_hours
    elapsed = hours_since_sunrise if daylight else hours_since_sunrise - day_hours
    third = min(2, int(elapsed / ((day_hours if daylight else 24-day_hours) / 3)))
    third_lord = ('Mercury', 'Sun', 'Saturn')[third] if daylight else ('Moon', 'Venus', 'Mars')[third]
    hora_order = ('Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon')
    hora_lord = hora_order[(hora_order.index(weekday_lord) + int(hours_since_sunrise)) % 7]
    out = {}
    for p in PLANETS:
        s = int(x[p] // 30)
        exalt = ZODIAC_SIGNS.index(EXALTATION[p][0])*30 + EXALTATION[p][1]
        uchcha = arc(x[p] - exalt - 180) / 3
        vargas = saptavargaja(x, p)
        parity = 1 if p in ('Moon', 'Venus') else 0
        oja = 15 * sum(division(x[p], d) % 2 == parity for d in (1, 9))
        house = (s - int(lagna % 360 // 30)) % 12
        kendra = (60, 30, 15)[house % 3]
        desired = 0 if p in ('Sun', 'Mars', 'Jupiter') else 2 if p in ('Moon', 'Venus') else 1
        drekkana = 15 if int(x[p] % 30 // 10) == desired else 0
        sthana = {'uchcha': uchcha, 'saptavargaja': sum(v['virupas'] for v in vargas.values()),
                  'ojayugmarasyamsa': oja, 'kendra': kendra, 'drekkana': drekkana}
        powerless = (mc+180 if p in ('Sun', 'Mars') else lagna+180 if p in ('Mercury', 'Jupiter')
                     else mc if p in ('Moon', 'Venus') else lagna)
        dig = arc(x[p]-powerless)/3
        natt = 60 if p == 'Mercury' else 5*natha_hours if p in ('Moon', 'Mars', 'Saturn') else 60-5*natha_hours
        paksha = phase if benefic.get(p, False) else 60-phase
        if p == 'Moon':
            paksha *= 2
        dec = krantis[p] if krantis is not None else kranti(x[p]+ayanamsa)
        signed = abs(dec) if p == 'Mercury' else -dec if p in ('Moon', 'Saturn') else dec
        ayana = (24+signed)*1.25*(2 if p == 'Sun' else 1)
        kala = {'natonnata': natt, 'paksha': paksha,
                'tribhaga': 60 if p in ('Jupiter', third_lord) else 0,
                'abda': 15 if p == year_lord else 0,
                'masa': 30 if p == month_lord else 0,
                'vara': 45 if p == weekday_lord else 0,
                'hora': 60 if p == hora_lord else 0, 'ayana': ayana, 'yuddha': 0}
        # Unwrap true longitude about mean longitude before taking the
        # average, avoiding a spurious half-circle at 0 Aries.
        mean = mean_longitudes.get(p, 0)
        mean_true = mean + ((x[p]-mean+180) % 360-180)/2
        chesta = 0 if p in ('Sun', 'Moon') else arc(seeghrochcha[p]-mean_true)/3
        aspects = {q: aspect_value(x[p]-x[q], q)*(1 if benefic.get(q, False) else -1)
                   for q in PLANETS if q != p}
        out[p] = {'sthana': sum(sthana.values()), 'sthana_components': sthana,
                  'saptavargaja_details': vargas, 'dig': dig,
                  'kala': sum(kala.values()), 'kala_components': kala,
                  'chesta': chesta, 'naisargika': NAISARGIKA[p],
                  'drik': sum(aspects.values())/4, 'drik_contributions': aspects}
        phala_chesta = arc(x[p]+ayanamsa+90)/3 if p == 'Sun' else phase if p == 'Moon' else chesta
        out[p]['phala_chesta'] = phala_chesta
        out[p]['ishta_phala'] = sqrt(uchcha*phala_chesta)
        out[p]['kashta_phala'] = sqrt(max(0, (60-uchcha)*(60-phala_chesta)))
    # Art.76 war uses the pre-ayana temporal subtotal, plus sthana and dig.
    diameters = {'Mars': 9.4, 'Mercury': 6.6, 'Jupiter': 190.4, 'Venus': 16.6, 'Saturn': 158}
    wars = []
    for i, p in enumerate(PLANETS[2:]):
        for q in PLANETS[2:][i+1:]:
            if arc(x[p]-x[q]) < 1:
                def subtotal(r):
                    row = out[r]
                    return row['sthana'] + row['dig'] + sum(v for k, v in row['kala_components'].items() if k not in ('ayana', 'yuddha'))
                amount = abs(subtotal(p)-subtotal(q))/abs(diameters[p]-diameters[q])
                # At the Aries wrap, the western body is still the victor.
                winner, loser = (p, q) if (x[q]-x[p]) % 360 < 180 else (q, p)
                out[winner]['kala_components']['yuddha'] += amount
                out[loser]['kala_components']['yuddha'] -= amount
                wars.append({'winner': winner, 'loser': loser, 'virupas': amount})
    for p, row in out.items():
        row['kala'] = sum(row['kala_components'].values())
        row['total_virupas'] = sum(row[k] for k in ('sthana', 'dig', 'kala', 'chesta', 'naisargika', 'drik'))
        row['total_rupas'] = row['total_virupas']/60
        row['required_rupas'] = REQUIRED[p]
        row['ratio'] = row['total_rupas']/REQUIRED[p]
        row['strong'] = row['ratio'] >= 1
    return {'engine': {'name': 'vedic.shadbala', 'version': '1.0.0', 'rules': {
                'method': SOURCE, 'units': 'virupas; 60 virupas per rupa',
                'sun_moon_chesta': 'zero in total; arts.136–137 values used only for phala',
                'mercury_association': 'same-sign malefic unless explicitly supplied',
                'kranti': 'Raman six-segment interpolation; latitude ignored'}},
            'warnings': ['Raman epoch mean-motion model is historical, not a modern orbital-element solution.'],
            'grahas': out, 'wars': wars,
            'inputs': {'longitudes': x, 'speeds': speeds, 'lagna': lagna, 'mc': mc,
                       'ayanamsa': ayanamsa, 'natha_hours': natha_hours,
                       'hours_since_sunrise': hours_since_sunrise, 'day_hours': day_hours,
                       'weekday_lord': weekday_lord, 'year_lord': year_lord,
                       'month_lord': month_lord, 'hora_lord': hora_lord,
                       'mean_longitudes': mean_longitudes, 'seeghrochcha': seeghrochcha,
                       'mercury_benefic': mercury_benefic, 'krantis': krantis}}
