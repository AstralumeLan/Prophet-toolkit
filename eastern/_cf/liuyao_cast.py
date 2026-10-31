# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations
from .utils import *
from .utils import xun_kong as utils_xun_kong
from .yijing_cast import *

EIGHT_PALACES: dict[str, list[tuple[int, str]]] = {
    # palace_name -> [(king_wen_num, role), ...]
    "乾宫": [
        (1, "本宫"), (44, "一世"), (33, "二世"), (12, "三世"),
        (20, "四世"), (23, "五世"), (35, "游魂"), (14, "归魂"),
    ],
    "兑宫": [
        (58, "本宫"), (47, "一世"), (45, "二世"), (31, "三世"),
        (39, "四世"), (15, "五世"), (62, "游魂"), (54, "归魂"),
    ],
    "离宫": [
        (30, "本宫"), (56, "一世"), (50, "二世"), (64, "三世"),
        (4,  "四世"), (59, "五世"), (6,  "游魂"), (13, "归魂"),
    ],
    "震宫": [
        (51, "本宫"), (16, "一世"), (40, "二世"), (32, "三世"),
        (46, "四世"), (48, "五世"), (28, "游魂"), (17, "归魂"),
    ],
    "巽宫": [
        (57, "本宫"), (9,  "一世"), (37, "二世"), (42, "三世"),
        (25, "四世"), (21, "五世"), (27, "游魂"), (18, "归魂"),
    ],
    "坎宫": [
        (29, "本宫"), (60, "一世"), (3,  "二世"), (63, "三世"),
        (49, "四世"), (55, "五世"), (36, "游魂"), (7,  "归魂"),
    ],
    "艮宫": [
        (52, "本宫"), (22, "一世"), (26, "二世"), (41, "三世"),
        (38, "四世"), (10, "五世"), (61, "游魂"), (53, "归魂"),
    ],
    "坤宫": [
        (2,  "本宫"), (24, "一世"), (19, "二世"), (11, "三世"),
        (34, "四世"), (43, "五世"), (5,  "游魂"), (8,  "归魂"),
    ],
}

ROLE_TO_SHIYAO: dict[str, int] = {
    "本宫": 6, "一世": 1, "二世": 2, "三世": 3,
    "四世": 4, "五世": 5, "游魂": 4, "归魂": 3,
}

def find_palace(hex_num: int) -> tuple[str | None, str | None]:
    for palace, entries in EIGHT_PALACES.items():
        for n, role in entries:
            if n == hex_num:
                return palace, role
    return None, None

def shi_yao_position(role: str) -> int:
    return ROLE_TO_SHIYAO.get(role, 0)

def ying_yao_position(shi: int) -> int:
    return ((shi - 1 + 3) % 6) + 1

NAJIA_TABLE: dict[str, dict] = {
    "乾": {"lower_stem": "甲", "upper_stem": "壬",
            "lower_branches": ["子", "寅", "辰"],
            "upper_branches": ["午", "申", "戌"]},
    "坎": {"lower_stem": "戊", "upper_stem": "戊",
            "lower_branches": ["寅", "辰", "午"],
            "upper_branches": ["申", "戌", "子"]},
    "艮": {"lower_stem": "丙", "upper_stem": "丙",
            "lower_branches": ["辰", "午", "申"],
            "upper_branches": ["戌", "子", "寅"]},
    "震": {"lower_stem": "庚", "upper_stem": "庚",
            "lower_branches": ["子", "寅", "辰"],
            "upper_branches": ["午", "申", "戌"]},
    "巽": {"lower_stem": "辛", "upper_stem": "辛",
            "lower_branches": ["丑", "亥", "酉"],
            "upper_branches": ["未", "巳", "卯"]},
    "离": {"lower_stem": "己", "upper_stem": "己",
            "lower_branches": ["卯", "丑", "亥"],
            "upper_branches": ["酉", "未", "巳"]},
    "坤": {"lower_stem": "乙", "upper_stem": "癸",
            "lower_branches": ["未", "巳", "卯"],
            "upper_branches": ["丑", "亥", "酉"]},
    "兑": {"lower_stem": "丁", "upper_stem": "丁",
            "lower_branches": ["巳", "卯", "丑"],
            "upper_branches": ["亥", "酉", "未"]},
}

def najia(upper_trigram: str, lower_trigram: str) -> list[dict]:
    """Return 6 entries bottom-to-top with stem+branch+wuxing each."""
    lt = NAJIA_TABLE[lower_trigram]
    ut = NAJIA_TABLE[upper_trigram]
    out: list[dict] = []
    for i in range(3):
        out.append({
            "position": i + 1,
            "stem": lt["lower_stem"],
            "branch": lt["lower_branches"][i],
            "wuxing": DIZHI_WUXING[lt["lower_branches"][i]],
        })
    for i in range(3):
        out.append({
            "position": 4 + i,
            "stem": ut["upper_stem"],
            "branch": ut["upper_branches"][i],
            "wuxing": DIZHI_WUXING[ut["upper_branches"][i]],
        })
    return out

def liu_qin(palace_wx: str, line_wx: str) -> str:
    if palace_wx == line_wx:
        return "兄弟"
    if WUXING_GEN.get(line_wx) == palace_wx:
        return "父母"  # line 五行 generates palace 五行 (生我)
    if WUXING_GEN.get(palace_wx) == line_wx:
        return "子孙"  # palace generates line (我生)
    if WUXING_KE.get(line_wx) == palace_wx:
        return "官鬼"  # line controls palace (克我)
    if WUXING_KE.get(palace_wx) == line_wx:
        return "妻财"
    return "未知"

LIU_SHEN_ORDER = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]

LIU_SHEN_START: dict[str, str] = {
    "甲": "青龙", "乙": "青龙",
    "丙": "朱雀", "丁": "朱雀",
    "戊": "勾陈",
    "己": "腾蛇",
    "庚": "白虎", "辛": "白虎",
    "壬": "玄武", "癸": "玄武",
}

def liu_shen(day_stem: str) -> list[str]:
    start_name = LIU_SHEN_START.get(day_stem, "青龙")
    start = LIU_SHEN_ORDER.index(start_name)
    return [LIU_SHEN_ORDER[(start + i) % 6] for i in range(6)]

def month_branch_season_wuxing(month_branch: str) -> str:
    return {
        "寅": "木", "卯": "木", "辰": "土",
        "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土",
        "亥": "水", "子": "水", "丑": "土",
    }[month_branch]

def wang_xiang(line_wx: str, season_wx: str) -> str:
    if line_wx == season_wx:
        return "旺"
    if WUXING_GEN.get(season_wx) == line_wx:
        return "相"
    if WUXING_GEN.get(line_wx) == season_wx:
        return "休"
    if WUXING_KE.get(line_wx) == season_wx:
        return "囚"
    if WUXING_KE.get(season_wx) == line_wx:
        return "死"
    return "?"

LIU_CHONG_PAIRS = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}

def xun_kong(day_stem: str, day_branch: str) -> list[str]:
    return utils_xun_kong(day_stem, day_branch)

def dress_chart(lines: list[int], day_stem: str, day_branch: str,
                month_branch: str, *, liu_qin_palace: str | None = None) -> dict:
    """Dress one hexagram, retaining the original palace for changed-line 六亲.

    Palace membership and 世应 still describe this hexagram's own 八宫 sequence.
    A nuclear/standalone chart uses its own palace unless explicitly supplied.
    """
    upper_bin, lower_bin = lines_to_trigrams(lines)
    hex_num, hex_name = hex_lookup_by_trigrams(upper_bin, lower_bin)
    upper_tri = BINARY_TO_TRIGRAM[upper_bin]
    lower_tri = BINARY_TO_TRIGRAM[lower_bin]
    palace, role = find_palace(hex_num)
    palace_wx = BAGUA[palace[:-1]]["wuxing"] if palace else None
    relative_palace = liu_qin_palace or palace
    relative_wx = BAGUA[relative_palace[:-1]]["wuxing"] if relative_palace else None
    shi = shi_yao_position(role) if role else 0
    ying = ying_yao_position(shi) if shi else 0

    nj = najia(upper_tri, lower_tri)
    ls = liu_shen(day_stem)
    season_wx = month_branch_season_wuxing(month_branch)
    kong = xun_kong(day_stem, day_branch)

    dressed_lines: list[dict] = []
    for i, line_v in enumerate(lines):
        b = nj[i]["branch"]
        wx = nj[i]["wuxing"]
        markers: list[str] = []
        if LIU_CHONG_PAIRS.get(b) == month_branch:
            markers.append("月破")
        if LIU_CHONG_PAIRS.get(b) == day_branch:
            markers.append("日破")
        if b in kong:
            markers.append("旬空")
        if line_v in (6, 9):
            markers.append("动爻")

        entry = {
            "position": i + 1,
            "value": line_v,
            "visual": line_visual(line_v),
            "stem": nj[i]["stem"],
            "branch": b,
            "wuxing": wx,
            "liu_qin": liu_qin(relative_wx, wx) if relative_wx else None,
            "liu_shen": ls[i],
            "state": wang_xiang(wx, season_wx),
            "is_shi": (i + 1 == shi),
            "is_ying": (i + 1 == ying),
            "markers": markers,
        }
        dressed_lines.append(entry)

    return {
        "hex_number": hex_num,
        "hex_name": hex_name,
        "upper_trigram": upper_tri,
        "lower_trigram": lower_tri,
        "palace": palace,
        "palace_wuxing": palace_wx,
        "palace_role": role,
        "liu_qin_basis": {
            "palace": relative_palace,
            "wuxing": relative_wx,
            "scope": "main_hexagram_palace" if liu_qin_palace else "own_hexagram_palace",
        },
        "shi_ying_basis": "own_hexagram_palace_sequence",
        "shi_position": shi,
        "ying_position": ying,
        "lines": dressed_lines,
    }

QUESTION_KEYWORDS = {
    "面试": "官鬼",
    "感情": "妻财 / 官鬼 (男看妻财, 女看官鬼)",
    "婚姻": "妻财 / 官鬼 (男看妻财, 女看官鬼)",
    "财运": "妻财",
    "事业": "官鬼",
    "工作": "官鬼",
    "考试": "父母 / 官鬼",
    "学业": "父母",
    "求名": "官鬼",
    "求子": "子孙",
    "健康": "子孙 (主医药)",
    "病": "官鬼 (病情) / 子孙 (医药)",
    "出行": "父母 (车船) / 兄弟 (同伴)",
    "求财": "妻财",
    "诉讼": "官鬼",
}

_GONGMING = {"passage_id": "zengshan:c008:p0001",
             "quote": "占功名、官府、雷霆鬼神、妻占夫皆以官鬼爻爲用神"}

_HUNYIN = {"passage_id": "zengshan:c034:p0129", "quote": "男卜女﹐姻財要旺。女占男﹐配鬼宜興。"}

_CAI = {"passage_id": "zengshan:c008:p0001", "quote": "占貨財、珠寶、倉庫一切使用之財物亦以妻財爻爲用神"}

YONGSHEN_SOURCES: dict[str, dict] = {
    "面试": {**_GONGMING, "mapping": "面试对应「功名」属现代类比，原文没有面试"},
    "事业": {**_GONGMING, "mapping": "事业对应「功名」属现代类比"},
    "工作": {**_GONGMING, "mapping": "工作对应「功名」属现代类比；问合同、待遇时对象不同"},
    "求名": {**_GONGMING, "mapping": "求名即功名"},
    "婚姻": {**_HUNYIN, "mapping": "原文即婚姻占"},
    "感情": {**_HUNYIN, "mapping": "感情对应婚姻占属现代类比"},
    "财运": {**_CAI, "mapping": "财运对应财物占属现代类比"},
    "求财": {**_CAI, "mapping": "原文即财物占"},
    "考试": {"passage_id": "zengshan:c033:p0574",
             "quote": "予見占功名必中者﹐卦象一成﹐若非旺父生身﹐定是旺官持世",
             "mapping": "考试对应科举功名属现代类比"},
    "学业": {"passage_id": "zengshan:c008:p0001", "quote": "文書及書館文契也以父母爻爲用神",
             "mapping": "学业对应文书、书馆属现代类比"},
    "求子": {"passage_id": "zengshan:c008:p0001",
             "quote": "占子孫、占女、女婿、侄、甥、門生凡在我子孫輩中皆以子孫爻爲用神",
             "mapping": "原文即子孙占"},
    "健康": {"passage_id": "zengshan:c008:p0001", "quote": "占忠臣、良將、醫藥、僧、道、兵卒皆以子孫爻爲用神",
             "mapping": "原文只说医药取子孙；不据此判断病情"},
    "病": {"passage_id": "zengshan:c034:p0368", "quote": "諸書無不以官爲鬼爲病﹐應爲醫人﹐子孫爲藥",
           "mapping": "同段野鶴随即反驳「此宜鬼者非鬼非病﹐乃憂神耳」；两说并列，不据此判断病情"},
}

LIU_QIN = ("父母", "兄弟", "子孙", "妻财", "官鬼")

POSITIONS = {1: "初爻", 2: "二爻", 3: "三爻", 4: "四爻", 5: "五爻", 6: "上爻"}

EPILOG = """Top-level JSON keys on stdout (UTF-8):
  method question entropy yongshen_hint yongshen_hint_source cast_time raw_lines main_chart
  changed_chart nuclear_chart active_lines main_judgment main_image
  active_line_text

On error: {"error": ..., "message": ...} and exit 1."""
