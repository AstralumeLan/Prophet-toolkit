# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations
import random
from .utils import *

KING_WEN_ORDER: list[tuple[int, str, int, int]] = [
    # (number, name, upper_binary, lower_binary)
    (1,  "乾为天",       0b111, 0b111),
    (2,  "坤为地",       0b000, 0b000),
    (3,  "水雷屯",       0b010, 0b100),
    (4,  "山水蒙",       0b001, 0b010),
    (5,  "水天需",       0b010, 0b111),
    (6,  "天水讼",       0b111, 0b010),
    (7,  "地水师",       0b000, 0b010),
    (8,  "水地比",       0b010, 0b000),
    (9,  "风天小畜",     0b011, 0b111),
    (10, "天泽履",       0b111, 0b110),
    (11, "地天泰",       0b000, 0b111),
    (12, "天地否",       0b111, 0b000),
    (13, "天火同人",     0b111, 0b101),
    (14, "火天大有",     0b101, 0b111),
    (15, "地山谦",       0b000, 0b001),
    (16, "雷地豫",       0b100, 0b000),
    (17, "泽雷随",       0b110, 0b100),
    (18, "山风蛊",       0b001, 0b011),
    (19, "地泽临",       0b000, 0b110),
    (20, "风地观",       0b011, 0b000),
    (21, "火雷噬嗑",     0b101, 0b100),
    (22, "山火贲",       0b001, 0b101),
    (23, "山地剥",       0b001, 0b000),
    (24, "地雷复",       0b000, 0b100),
    (25, "天雷无妄",     0b111, 0b100),
    (26, "山天大畜",     0b001, 0b111),
    (27, "山雷颐",       0b001, 0b100),
    (28, "泽风大过",     0b110, 0b011),
    (29, "坎为水",       0b010, 0b010),
    (30, "离为火",       0b101, 0b101),
    (31, "泽山咸",       0b110, 0b001),
    (32, "雷风恒",       0b100, 0b011),
    (33, "天山遁",       0b111, 0b001),
    (34, "雷天大壮",     0b100, 0b111),
    (35, "火地晋",       0b101, 0b000),
    (36, "地火明夷",     0b000, 0b101),
    (37, "风火家人",     0b011, 0b101),
    (38, "火泽睽",       0b101, 0b110),
    (39, "水山蹇",       0b010, 0b001),
    (40, "雷水解",       0b100, 0b010),
    (41, "山泽损",       0b001, 0b110),
    (42, "风雷益",       0b011, 0b100),
    (43, "泽天夬",       0b110, 0b111),
    (44, "天风姤",       0b111, 0b011),
    (45, "泽地萃",       0b110, 0b000),
    (46, "地风升",       0b000, 0b011),
    (47, "泽水困",       0b110, 0b010),
    (48, "水风井",       0b010, 0b011),
    (49, "泽火革",       0b110, 0b101),
    (50, "火风鼎",       0b101, 0b011),
    (51, "震为雷",       0b100, 0b100),
    (52, "艮为山",       0b001, 0b001),
    (53, "风山渐",       0b011, 0b001),
    (54, "雷泽归妹",     0b100, 0b110),
    (55, "雷火丰",       0b100, 0b101),
    (56, "火山旅",       0b101, 0b001),
    (57, "巽为风",       0b011, 0b011),
    (58, "兑为泽",       0b110, 0b110),
    (59, "风水涣",       0b011, 0b010),
    (60, "水泽节",       0b010, 0b110),
    (61, "风泽中孚",     0b011, 0b110),
    (62, "雷山小过",     0b100, 0b001),
    (63, "水火既济",     0b010, 0b101),
    (64, "火水未济",     0b101, 0b010),
]

def hex_lookup_by_trigrams(upper_bin: int, lower_bin: int) -> tuple[int, str]:
    """Look up Kingwen #, name by (upper_binary, lower_binary)."""
    for n, name, up, low in KING_WEN_ORDER:
        if up == upper_bin and low == lower_bin:
            return n, name
    return 0, "未知卦"

YAO_POSITION_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

def cast_coins(rng: random.Random) -> list[int]:
    """Return list of 6 line values bottom-to-top."""
    lines: list[int] = []
    for _ in range(6):
        total = sum(rng.choice([2, 3]) for _ in range(3))
        lines.append(total)
    return lines

def from_numbers(upper: int, lower: int, change: int) -> list[int]:
    upper = ((upper - 1) % 8) + 1
    lower = ((lower - 1) % 8) + 1
    change = ((change - 1) % 6) + 1
    upper_tri = XIANTIAN_NUM_TO_TRIGRAM[upper]
    lower_tri = XIANTIAN_NUM_TO_TRIGRAM[lower]

    # Build 6 lines bottom -> top, using static 7/8 then set the changing line.
    upper_bin = BAGUA[upper_tri]["binary"]
    lower_bin = BAGUA[lower_tri]["binary"]
    lines: list[int] = []
    # BAGUA["binary"] encodes the trigram top-to-bottom, so bit 2 is 初爻.
    # Emit bottom-to-top: line 1,2,3 = bits 2,1,0.
    for i in range(3):
        bit = (lower_bin >> (2 - i)) & 1
        lines.append(7 if bit == 1 else 8)
    for i in range(3):
        bit = (upper_bin >> (2 - i)) & 1
        lines.append(7 if bit == 1 else 8)
    # apply changing line: convert static -> moving (7 -> 9, 8 -> 6)
    idx = change - 1
    if lines[idx] == 7:
        lines[idx] = 9
    else:
        lines[idx] = 6
    return lines

def line_visual(v: int) -> str:
    # 6 (老阴): ━ ━ x   (changing yin)
    # 7 (少阳): ━━━
    # 8 (少阴): ━ ━
    # 9 (老阳): ━━━ o   (changing yang)
    if v == 6:
        return "━  ━  ✕"
    if v == 7:
        return "━━━━━"
    if v == 8:
        return "━  ━"
    if v == 9:
        return "━━━━━  ○"
    return "?"

def lines_to_trigrams(lines: list[int]) -> tuple[int, int]:
    """Return (upper_bin, lower_bin) in BAGUA["binary"] convention.

    `lines` runs bottom-to-top (index 0 = 初爻); BAGUA encodes each trigram
    top-to-bottom, so 初爻 is bit 2, not bit 0."""
    lower_bin = 0
    for i in range(3):
        if lines[i] in (7, 9):  # yang
            lower_bin |= 1 << (2 - i)
    upper_bin = 0
    for i in range(3):
        if lines[3 + i] in (7, 9):
            upper_bin |= 1 << (2 - i)
    return upper_bin, lower_bin

def changed_lines(lines: list[int]) -> list[int]:
    """Return new line values after applying 老阴/老阳 transforms."""
    out: list[int] = []
    for v in lines:
        if v == 6:
            out.append(7)  # 老阴变少阳
        elif v == 9:
            out.append(8)  # 老阳变少阴
        else:
            out.append(v)
    return out

def nuclear_lines(lines: list[int]) -> list[int]:
    """Compute 互卦 lines (use yin/yang only, ignore changing markers)."""
    yy = [1 if v in (7, 9) else 0 for v in lines]
    # 互卦: 下卦 = 2,3,4 爻; 上卦 = 3,4,5 爻
    new_yy = [yy[1], yy[2], yy[3], yy[2], yy[3], yy[4]]
    return [7 if b == 1 else 8 for b in new_yy]

def active_lines(lines: list[int]) -> list[int]:
    return [i + 1 for i, v in enumerate(lines) if v in (6, 9)]

EPILOG = """Top-level JSON keys on stdout (UTF-8):
  method question meta raw_lines main_hex changed_hex nuclear_hex
  active_lines active_line_text summary

*_hex: number name upper_trigram lower_trigram lines lines_visual
  judgment image

lines_visual is drawn 上爻-first with each row labelled; lines[] and
  active_lines number 初爻 = 1 from the bottom.

lookup --number N: number name name_short name_en judgment image lines summary
lookup --all:      hexagrams[] of the above

On error: {"error": ..., "message": ...} and exit 1."""
