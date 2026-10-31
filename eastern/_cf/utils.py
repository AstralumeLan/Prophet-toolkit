# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations
from datetime import timezone as _timezone
UTC = _timezone.utc

UTC = _timezone.utc

VENDORED_MISSING = ("scripts/ 里随包的 lunar_python 不见了：请重新下载完整的 chinese-fortune "
                    "发布包或仓库，不需要 pip 安装")

TIANGAN: list[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

DIZHI: list[str] = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]

TIANGAN_YIN_YANG: dict[str, str] = {
    s: ("阳" if i % 2 == 0 else "阴") for i, s in enumerate(TIANGAN)
}

DIZHI_YIN_YANG: dict[str, str] = {
    b: ("阳" if i % 2 == 0 else "阴") for i, b in enumerate(DIZHI)
}

TIANGAN_WUXING: dict[str, str] = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

DIZHI_WUXING: dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

WUXING: dict[str, str] = {**TIANGAN_WUXING, **DIZHI_WUXING}

WUXING_GEN: dict[str, str] = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木",
}

WUXING_KE: dict[str, str] = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木",
}

DIZHI_ZODIAC: dict[str, str] = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
    "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪",
}

ZODIAC_TO_DIZHI: dict[str, str] = {v: k for k, v in DIZHI_ZODIAC.items()}

HIDDEN_STEMS: dict[str, list[str]] = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

__version__ = "5.9.1"

BAGUA: dict[str, dict] = {
    "乾": {"lines": [1, 1, 1], "binary": 0b111, "wuxing": "金",
            "nature": "天", "attribute": "健", "direction_houtian": "西北",
            "family": "父", "number_xiantian": 1},
    "兑": {"lines": [0, 1, 1], "binary": 0b110, "wuxing": "金",
            "nature": "泽", "attribute": "悦", "direction_houtian": "西",
            "family": "少女", "number_xiantian": 2},
    "离": {"lines": [1, 0, 1], "binary": 0b101, "wuxing": "火",
            "nature": "火", "attribute": "丽", "direction_houtian": "南",
            "family": "中女", "number_xiantian": 3},
    "震": {"lines": [0, 0, 1], "binary": 0b100, "wuxing": "木",
            "nature": "雷", "attribute": "动", "direction_houtian": "东",
            "family": "长男", "number_xiantian": 4},
    "巽": {"lines": [1, 1, 0], "binary": 0b011, "wuxing": "木",
            "nature": "风", "attribute": "入", "direction_houtian": "东南",
            "family": "长女", "number_xiantian": 5},
    "坎": {"lines": [0, 1, 0], "binary": 0b010, "wuxing": "水",
            "nature": "水", "attribute": "陷", "direction_houtian": "北",
            "family": "中男", "number_xiantian": 6},
    "艮": {"lines": [1, 0, 0], "binary": 0b001, "wuxing": "土",
            "nature": "山", "attribute": "止", "direction_houtian": "东北",
            "family": "少男", "number_xiantian": 7},
    "坤": {"lines": [0, 0, 0], "binary": 0b000, "wuxing": "土",
            "nature": "地", "attribute": "顺", "direction_houtian": "西南",
            "family": "母", "number_xiantian": 8},
}

XIANTIAN_NUM_TO_TRIGRAM: dict[int, str] = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤",
}

BINARY_TO_TRIGRAM: dict[int, str] = {v["binary"]: k for k, v in BAGUA.items()}

WUHU_DUN: dict[str, str] = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

WUSHU_DUN: dict[str, str] = {
    "甲": "甲", "己": "甲",
    "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊",
    "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}

XUN_KONG_BY_OFFSET: dict[int, list[str]] = {
    0: ["戌", "亥"],   # 甲子旬
    1: ["申", "酉"],   # 甲戌旬
    2: ["午", "未"],   # 甲申旬
    3: ["辰", "巳"],   # 甲午旬
    4: ["寅", "卯"],   # 甲辰旬
    5: ["子", "丑"],   # 甲寅旬
}

_XUN_DIFF_TO_OFFSET: dict[int, int] = {0: 0, 10: 1, 8: 2, 6: 3, 4: 4, 2: 5}

def xun_kong(stem: str, branch: str) -> list[str]:
    """The two 地支 that are 旬空 for a given 干支 pillar.

    Every 旬 covers 10 of the 12 branches; the two left over are 空亡. bazi and
    liuyao carried identical copies of this table, verified equal across all 60
    pillars before merging.
    """
    diff = (DIZHI.index(branch) - TIANGAN.index(stem)) % 12
    offset = _XUN_DIFF_TO_OFFSET.get(diff)
    return XUN_KONG_BY_OFFSET[offset] if offset is not None else []

def hour_branch_index(hour: int) -> int:
    """0-11 index of the 时辰 containing ``hour`` (子=0).

    子时 spans 23:00-01:00, so both 23 and 0 map to 子. Five engines carried
    byte-identical copies of this arithmetic; they now share this one, which is
    verified against all 24 hours in tests/test_utils.py.
    """
    if hour == 23 or hour == 0:
        return 0
    return ((hour + 1) // 2) % 12

def shichen_number(hour: int) -> int:
    """1-based 时辰 ordinal (子=1 … 亥=12), as 梅花/周易 起卦 expects."""
    return hour_branch_index(hour) + 1

def jiazi_index(stem: str, branch: str) -> int:
    """Return 0-59 index of a 甲子 pair."""
    s = TIANGAN.index(stem)
    b = DIZHI.index(branch)
    # The 60-cycle: stems repeat every 10, branches every 12; offset must satisfy
    # both. Walk the cycle until match.
    for i in range(60):
        if i % 10 == s and i % 12 == b:
            return i
    raise ValueError(f"invalid 甲子 pair: {stem}{branch}")

YEAR_MIN, YEAR_MAX = 1900, 2100

_CITY_INDEX: dict[str, dict] | None = None

def require_lunar():
    import lunar_python
    return lunar_python
