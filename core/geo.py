"""地点 → 经纬度（手填常量表，离线）。仅收录通用的大城市中心坐标（市级近似）；其他地点请用 --lat/--lon/--tz。"""
from __future__ import annotations

PLACES: dict[str, dict] = {
    "北京": {"lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai", "精度": "市级近似"},
    "上海": {"lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai", "精度": "市级近似"},
    "广州": {"lat": 23.1291, "lon": 113.2644, "tz": "Asia/Shanghai", "精度": "市级近似"},
    "成都": {"lat": 30.5728, "lon": 104.0668, "tz": "Asia/Shanghai", "精度": "市级近似"},
    "西安": {"lat": 34.3416, "lon": 108.9398, "tz": "Asia/Shanghai", "精度": "市级近似"},
    "台北": {"lat": 25.0330, "lon": 121.5654, "tz": "Asia/Taipei", "精度": "市级近似"},
    "东京": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo", "精度": "市级近似"},
    "首尔": {"lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul", "精度": "市级近似"},
    "新加坡": {"lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "精度": "市级近似"},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "精度": "city"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata", "精度": "city"},
    "London": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "精度": "city"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris", "精度": "city"},
    "Berlin": {"lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin", "精度": "city"},
    "Ulm": {"lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin", "精度": "city"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "精度": "city"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "精度": "city"},
}
ALIASES = {
    "北京市": "北京", "beijing": "北京", "上海市": "上海", "shanghai": "上海", "广州市": "广州", "guangzhou": "广州",
    "成都市": "成都", "西安市": "西安", "台北市": "台北", "taipei": "台北", "东京都": "东京", "tokyo": "东京",
    "seoul": "首尔", "singapore": "新加坡", "delhi": "New Delhi", "new delhi": "New Delhi", "新德里": "New Delhi",
    "bangalore": "Bengaluru", "bengaluru": "Bengaluru", "班加罗尔": "Bengaluru",
    "london": "London", "伦敦": "London", "paris": "Paris", "巴黎": "Paris", "berlin": "Berlin", "柏林": "Berlin",
    "ulm": "Ulm", "乌尔姆": "Ulm", "new york": "New York", "纽约": "New York", "sydney": "Sydney", "悉尼": "Sydney",
}


def lookup(name: str) -> dict:
    key = name.strip()
    k = key if key in PLACES else ALIASES.get(key, ALIASES.get(key.lower()))
    if k is None or k not in PLACES:
        raise KeyError(f"未知地点：{name}；可用：{', '.join(PLACES)}；或改用 --lat/--lon/--tz")
    return {"地点": k, "输入": name, **PLACES[k]}


def register(sub):
    p = sub.add_parser("geo", help="地点→经纬度（常量表）")
    p.add_argument("place", nargs="?", help="地点名；省略则列出全部")
    p.set_defaults(func=lambda a: lookup(a.place) if a.place else {"places": PLACES, "aliases": ALIASES})
