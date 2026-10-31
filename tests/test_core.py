from types import SimpleNamespace as NS
from core.inputs import resolve_birth, shichen_candidates, load_people
from core.solartime import true_solar
from datetime import datetime


def _a(**kw):
    base = dict(person=None, date=None, time=None, time_range=None, place=None, lat=None, lon=None, tz=None, gender=None)
    base.update(kw); return NS(**base)


def test_people_s01_s04_raw_values():
    ps = {p["代号"]: p for p in load_people()}
    assert set(ps) >= {"S01", "S02", "S03", "S04"}
    assert ps["S01"]["原始当地日期"] == "1990-03-15" and ps["S01"]["原始当地时间"] == "08:45"
    assert ps["S02"]["时间精度"]["区间"] == ["20:00", "21:00"] and ps["S02"]["原始当地时间"] is None
    assert ps["S02"]["原始当地日期"] == "1975-11-02"
    assert ps["S03"]["原始当地时间"] == "14:10" and ps["S03"]["时间精度"]["类型"] == "provisional"
    assert ps["S04"]["时间精度"]["类型"] == "approx"


def test_true_solar_s01_beijing_correction():
    r = true_solar(datetime(1990, 3, 15, 8, 45), 116.4074, "Asia/Shanghai")
    assert r["原始钟表时间"] == "1990-03-15 08:45:00"
    # Frozen fictional S01 result; NOAA independently checks EOT below.
    assert r["真太阳时"].startswith('1990-03-15 08:21')
    assert abs(r["经度差校正分钟"] - 4*(116.4074-120)) < .001
    assert abs(r["均时差分钟"] - r["均时差分钟_NOAA校验"]) < 1.0


def test_true_solar_eot_reference_feb_nov():
    # 均时差公认极值：2月中约 -14.2 分，11月初约 +16.4 分
    from core.solartime import eot_minutes_swe
    assert -14.6 < eot_minutes_swe(datetime(2020, 2, 11, 12)) < -13.9
    assert 16.2 < eot_minutes_swe(datetime(2020, 11, 3, 12)) < 16.6


def test_china_dst_1988_offset():
    r = true_solar(datetime(1988, 7, 1, 12, 0), 120.0, "Asia/Shanghai")
    assert r["夏令时"] is True and r["UTC偏移分钟"] == 540


def test_approx_range_shichen_branching():
    b = resolve_birth(_a(person="S02"))
    assert b["time"] is None and b["time_range"] == ["20:00", "21:00"]
    scs = [c["shichen"] for c in shichen_candidates(b)]
    assert scs == ["戌", "亥"]  # 21:00 端点进入亥时
    b2 = resolve_birth(_a(date="2000-01-01", time_range="10:30-13:30", place="北京"))
    assert [c["shichen"] for c in shichen_candidates(b2)] == ["巳", "午", "未"]
