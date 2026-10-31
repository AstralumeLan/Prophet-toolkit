"""真太阳时：经度差 + 均时差（swisseph swe.time_equ；NOAA 公式作交叉校验）。原值不覆盖。"""
from __future__ import annotations
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

ENGINE = {"name": "core.solartime", "version": "1.0.0", "eot": "swisseph.time_equ (Moshier)", "check": "NOAA approx"}


def _utc(local: datetime, tz: str) -> datetime:
    return local.replace(tzinfo=ZoneInfo(tz)).astimezone(ZoneInfo("UTC"))


def eot_minutes_swe(utc: datetime) -> float:
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)
    e = swe.time_equ(jd)
    e = e[0] if isinstance(e, (tuple, list)) else e
    return e * 1440.0


def eot_minutes_noaa(utc: datetime) -> float:
    doy = utc.timetuple().tm_yday
    g = 2 * math.pi / 365 * (doy - 1 + (utc.hour - 12) / 24)
    return 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                     - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))


def true_solar(local: datetime, lon: float, tz: str) -> dict:
    """local: naive clock datetime in tz. Returns dict with original and corrected values."""
    aware = local.replace(tzinfo=ZoneInfo(tz))
    off_min = aware.utcoffset().total_seconds() / 60
    dst = bool(aware.dst())
    utc = _utc(local, tz)
    lmt_shift = lon * 4 - off_min  # minutes: local mean time - clock
    eot = eot_minutes_swe(utc)
    eot2 = eot_minutes_noaa(utc)
    tst = local + timedelta(minutes=lmt_shift + eot)
    return {
        "原始钟表时间": local.strftime("%Y-%m-%d %H:%M:%S"),
        "时区": tz, "UTC偏移分钟": off_min, "夏令时": dst,
        "UTC": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "经度": lon,
        "经度差校正分钟": round(lmt_shift, 3),
        "均时差分钟": round(eot, 3),
        "均时差分钟_NOAA校验": round(eot2, 3),
        "总校正分钟": round(lmt_shift + eot, 3),
        "真太阳时": tst.strftime("%Y-%m-%d %H:%M:%S"),
        "engine": ENGINE,
    }


def register(sub):
    p = sub.add_parser("solartime", help="真太阳时计算（保留原值）")
    from core.inputs import add_birth_args, resolve_birth
    add_birth_args(p)

    def run(a):
        b = resolve_birth(a)
        out = {"person": b.get("代号"), "input": b, "results": []}
        for c in b["candidates"]:
            out["results"].append({"候选": c["label"], **true_solar(c["dt"], b["lon"], b["tz"])})
        return out
    p.set_defaults(func=run)
