"""统一出生/起卦输入解析：--person Sxx 或 --date/--time/--place（或 --lat/--lon/--tz）临时输入。

约略时间（approx）以区间保存，从不取中点为“确认时间”；需要具体时刻的引擎通过
shichen_candidates()/sample_candidates() 取计算用候选，并在输出中标注候选性质。
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta
from pathlib import Path

from core import geo

ROOT = Path(__file__).resolve().parent.parent
PEOPLE_PRIVATE = ROOT / "core" / "people.json"          # 私人档案（gitignored，绝不提交）
PEOPLE_EXAMPLE = ROOT / "core" / "people.example.json"  # 虚构示例
PEOPLE = PEOPLE_PRIVATE if PEOPLE_PRIVATE.exists() else PEOPLE_EXAMPLE
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
GENDER = {"男": "male", "女": "female", "male": "male", "female": "female", "m": "male", "f": "female"}


def load_people() -> list[dict]:
    return json.loads(PEOPLE.read_text(encoding="utf-8"))["people"]


def get_person(code: str) -> dict:
    for p in load_people():
        if p["代号"].upper() == code.upper():
            return p
    raise KeyError(f"未知人物代号 {code}")


def add_birth_args(p, gender_required: bool = False):
    g = p.add_argument_group("输入（--person 或临时输入）")
    g.add_argument("--person", help="人物代号，如 S01（core/people.json，缺省时用虚构示例 core/people.example.json）")
    g.add_argument("--date", help="公历日期 YYYY-MM-DD")
    g.add_argument("--time", help="当地钟表时间 HH:MM")
    g.add_argument("--time-range", help="约略时间区间 HH:MM-HH:MM（覆盖人物档案的区间）")
    g.add_argument("--place", help="地点名（core/geo 常量表）")
    g.add_argument("--lat", type=float)
    g.add_argument("--lon", type=float)
    g.add_argument("--tz", help="IANA 时区，如 Asia/Shanghai")
    g.add_argument("--gender", choices=["male", "female", "男", "女"])
    g.add_argument("--json", action="store_true", help="输出 JSON（默认即 JSON，保留兼容）")
    return p


def _parse_hm(s: str) -> tuple[int, int]:
    h, m = s.strip().split(":")[:2]
    return int(h), int(m)


def resolve_birth(a) -> dict:
    """Return a dict describing the input; `candidates` is a list of {label, dt, kind}."""
    person = None
    if getattr(a, "person", None):
        person = get_person(a.person)
    date = getattr(a, "date", None) or (person and person["原始当地日期"])
    if not date:
        raise ValueError("需要 --person 或 --date")
    time = getattr(a, "time", None) or (person and person.get("原始当地时间"))
    prec = (person or {}).get("时间精度", {"类型": "exact" if time else "unknown"})
    rng = None
    if getattr(a, "time_range", None):
        s, e = a.time_range.split("-")
        rng = [s.strip(), e.strip()]
        prec = {"类型": "approx", "区间": rng, "说明": "命令行 --time-range"}
        time = None
    elif prec.get("类型") == "approx":
        rng = prec["区间"]
        time = None
    place = getattr(a, "place", None) or (person and person.get("geo_key"))
    lat, lon, tz = getattr(a, "lat", None), getattr(a, "lon", None), getattr(a, "tz", None)
    geo_info = None
    if place and (lat is None or lon is None):
        geo_info = geo.lookup(place)
        lat = geo_info["lat"] if lat is None else lat
        lon = geo_info["lon"] if lon is None else lon
        tz = tz or geo_info["tz"]
    tz = tz or (person and person.get("时区")) or "Asia/Shanghai"
    if lat is None or lon is None:
        raise ValueError("需要地点：--place 或 --lat/--lon")
    g = getattr(a, "gender", None) or (person and person.get("性别"))
    gender = GENDER.get(g) if g else None
    y, mo, d = (int(x) for x in date.split("-"))
    out = {
        "代号": person["代号"] if person else None,
        "称呼": person["称呼"] if person else None,
        "gender": gender, "date": date, "time": time, "time_range": rng,
        "时间精度": prec, "place": place, "geo": geo_info,
        "lat": lat, "lon": lon, "tz": tz,
    }
    if rng:
        sh, sm = _parse_hm(rng[0]); eh, em = _parse_hm(rng[1])
        start = datetime(y, mo, d, sh, sm)
        end = datetime(y, mo, d, eh, em)
        if end < start:
            end += timedelta(days=1)
        out["range_dt"] = [start, end]
        out["candidates"] = [
            {"label": f"区间起点 {rng[0]}", "dt": start, "kind": "range-start"},
            {"label": f"区间终点 {rng[1]}", "dt": end, "kind": "range-end"},
        ]
    elif time:
        h, m = _parse_hm(time)
        out["candidates"] = [{"label": f"{time}（{prec.get('类型')}）", "dt": datetime(y, mo, d, h, m), "kind": prec.get("类型", "exact")}]
    else:
        out["candidates"] = [{"label": "时间未知：中午占位，仅日级结果可用", "dt": datetime(y, mo, d, 12, 0), "kind": "unknown-noon"}]
        out["时间精度"] = {"类型": "unknown"}
    return out


def shichen_of(dt: datetime) -> str:
    return BRANCHES[((dt.hour + 1) // 2) % 12]


def shichen_candidates(b: dict, true_solar: bool = False) -> list[dict]:
    """One computation sample per distinct 时辰 covered by the input (minute scan).

    Each sample is the middle of the covered sub-interval (a computation sample, NOT a claimed birth time).
    When true_solar=True the 时辰 is judged on true solar time (core.solartime).
    """
    if not b.get("range_dt"):
        c = b["candidates"][0]
        return [dict(c, shichen=shichen_of(_ts(c["dt"], b) if true_solar else c["dt"]))]
    start, end = b["range_dt"]
    segs: list[list] = []
    t = start
    while t <= end:
        judge = _ts(t, b) if true_solar else t
        sc = shichen_of(judge)
        if segs and segs[-1][0] == sc:
            segs[-1][2] = t
        else:
            segs.append([sc, t, t])
        t += timedelta(minutes=1)
    out = []
    for sc, s, e in segs:
        mid = s + (e - s) / 2
        mid = mid.replace(second=0, microsecond=0)
        out.append({"label": f"{sc}时候选（钟表 {s:%H:%M}–{e:%H:%M}）", "dt": mid, "kind": "shichen-sample",
                    "shichen": sc, "clock_span": [f"{s:%H:%M}", f"{e:%H:%M}"],
                    "note": "计算取样点，非确认出生时间" + ("；仅区间端点" if s == e else "")})
    return out


def sample_candidates(b: dict, step_min: int = 15) -> list[dict]:
    """Regular samples across an approx range (for ascendant-sensitive western/vedic charts)."""
    if not b.get("range_dt"):
        return b["candidates"]
    start, end = b["range_dt"]
    out, t = [], start
    while t <= end:
        out.append({"label": f"取样 {t:%H:%M}", "dt": t, "kind": "range-sample", "note": "计算取样点，非确认出生时间"})
        t += timedelta(minutes=step_min)
    if out[-1]["dt"] != end:
        out.append({"label": f"取样 {end:%H:%M}", "dt": end, "kind": "range-sample", "note": "区间终点"})
    return out


def _ts(dt: datetime, b: dict) -> datetime:
    from core.solartime import true_solar
    return datetime.strptime(true_solar(dt, b["lon"], b["tz"])["真太阳时"], "%Y-%m-%d %H:%M:%S")


def invariants(results: list[dict], keys: list[str] | None = None) -> dict:
    """Given per-candidate flat dicts, report which keys are identical across all candidates."""
    if not results:
        return {}
    keys = keys or list(results[0].keys())
    stable, varying = {}, {}
    for k in keys:
        vals = [json.dumps(r.get(k), ensure_ascii=False, sort_keys=True, default=str) for r in results]
        if len(set(vals)) == 1:
            stable[k] = results[0].get(k)
        else:
            varying[k] = [r.get(k) for r in results]
    return {"不随时间变化": stable, "随时间变化": varying}


def register(sub):
    p = sub.add_parser("person", help="人物档案")
    sp = p.add_subparsers(dest="sub", required=True)
    ls = sp.add_parser("list"); ls.set_defaults(func=lambda a: {"people": load_people()})
    sh = sp.add_parser("show"); sh.add_argument("code")
    sh.set_defaults(func=lambda a: get_person(a.code))
    rs = sp.add_parser("resolve", help="解析输入并列出候选时刻")
    add_birth_args(rs)
    rs.add_argument("--true-solar", action="store_true")

    def _res(a):
        b = resolve_birth(a)
        b["shichen_candidates"] = shichen_candidates(b, true_solar=a.true_solar)
        return b
    rs.set_defaults(func=_res)
