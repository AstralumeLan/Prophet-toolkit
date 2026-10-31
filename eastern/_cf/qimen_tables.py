# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations


PALACE_INFO: dict[int, dict[str, str]] = {
    1: {"palace": "坎", "direction": "北",   "wuxing": "水"},
    2: {"palace": "坤", "direction": "西南", "wuxing": "土"},
    3: {"palace": "震", "direction": "东",   "wuxing": "木"},
    4: {"palace": "巽", "direction": "东南", "wuxing": "木"},
    5: {"palace": "中", "direction": "中央", "wuxing": "土"},
    6: {"palace": "乾", "direction": "西北", "wuxing": "金"},
    7: {"palace": "兑", "direction": "西",   "wuxing": "金"},
    8: {"palace": "艮", "direction": "东北", "wuxing": "土"},
    9: {"palace": "离", "direction": "南",   "wuxing": "火"},
}

YANG_PALACE_SEQ: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]

YIN_PALACE_SEQ: list[int] = [9, 8, 7, 6, 5, 4, 3, 2, 1]

MEN_HOME_PALACE: dict[str, int] = {
    "休门": 1, "死门": 2, "伤门": 3, "杜门": 4,
    "开门": 6, "惊门": 7, "生门": 8, "景门": 9,
}

MEN_ORDER_BY_PALACE: list[tuple[int, str]] = [
    (1, "休门"), (8, "生门"), (3, "伤门"), (4, "杜门"),
    (9, "景门"), (2, "死门"), (7, "惊门"), (6, "开门"),
]

STAR_ORDER_BY_PALACE: list[tuple[int, str]] = [
    (1, "天蓬"), (8, "天任"), (3, "天冲"), (4, "天辅"),
    (9, "天英"), (2, "天芮"), (7, "天柱"), (6, "天心"),
    (5, "天禽"),
]

STAR_HOME_PALACE: dict[str, int] = {name: pal for pal, name in STAR_ORDER_BY_PALACE}

EIGHT_SHEN_ORDER: list[str] = [
    "值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天",
]

SAN_QI: list[str] = ["乙", "丙", "丁"]

LIU_YI: list[str] = ["戊", "己", "庚", "辛", "壬", "癸"]

YIQI_ORDER: list[str] = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

YANG_JIE_QI: dict[str, tuple[int, int, int]] = {
    # (上元局, 中元局, 下元局)
    "冬至": (1, 7, 4),
    "小寒": (2, 8, 5),
    "大寒": (3, 9, 6),
    "立春": (8, 5, 2),
    "雨水": (9, 6, 3),
    "惊蛰": (1, 7, 4),
    "春分": (3, 9, 6),
    "清明": (4, 1, 7),
    "谷雨": (5, 2, 8),
    "立夏": (4, 1, 7),
    "小满": (5, 2, 8),
    "芒种": (6, 3, 9),
}

YIN_JIE_QI: dict[str, tuple[int, int, int]] = {
    "夏至": (9, 3, 6),
    "小暑": (8, 2, 5),
    "大暑": (7, 1, 4),
    "立秋": (2, 5, 8),
    "处暑": (1, 4, 7),
    "白露": (9, 3, 6),
    "秋分": (7, 1, 4),
    "寒露": (6, 9, 3),
    "霜降": (5, 8, 2),
    "立冬": (6, 9, 3),
    "小雪": (5, 8, 2),
    "大雪": (4, 7, 1),
}

XUN_HEADS: list[tuple[str, str]] = [
    ("甲子", "戊"),   # 戊 represents 甲子旬
    ("甲戌", "己"),
    ("甲申", "庚"),
    ("甲午", "辛"),
    ("甲辰", "壬"),
    ("甲寅", "癸"),
]
