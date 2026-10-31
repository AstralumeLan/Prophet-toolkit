# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations
from .utils import *
from .yijing_cast import *
from .classical_time_numbers import time_numbers

def build_lines(upper_tri: str, lower_tri: str, change_line: int) -> list[int]:
    upper_bin = BAGUA[upper_tri]["binary"]
    lower_bin = BAGUA[lower_tri]["binary"]
    lines: list[int] = []
    # BAGUA["binary"] is top-to-bottom, so 初爻 is bit 2 (see yijing_cast).
    for i in range(3):
        lines.append(7 if (lower_bin >> (2 - i)) & 1 else 8)
    for i in range(3):
        lines.append(7 if (upper_bin >> (2 - i)) & 1 else 8)
    idx = change_line - 1
    lines[idx] = 9 if lines[idx] == 7 else 6
    return lines

def ti_yong(upper_tri: str, lower_tri: str, change_line: int) -> tuple[str, str]:
    if 1 <= change_line <= 3:
        return upper_tri, lower_tri  # 体 = upper, 用 = lower (动在下)
    return lower_tri, upper_tri

def ti_yong_relation(ti_tri: str, yong_tri: str) -> str:
    ti_wx = BAGUA[ti_tri]["wuxing"]
    yong_wx = BAGUA[yong_tri]["wuxing"]
    if ti_wx == yong_wx:
        return "比和"
    if WUXING_GEN.get(yong_wx) == ti_wx:
        return "用生体 (吉)"
    if WUXING_GEN.get(ti_wx) == yong_wx:
        return "体生用 (耗体)"
    if WUXING_KE.get(yong_wx) == ti_wx:
        return "用克体 (凶)"
    if WUXING_KE.get(ti_wx) == yong_wx:
        return "体克用 (吉)"
    return "未知"

SEASON_WX_BY_MONTH: dict[int, str] = {
    # 公历月 -> 当令五行 (对应 寅卯/巳午/申酉/亥子 四组 + 辰未戌丑 四季月)
    2: "木", 3: "木",
    5: "火", 6: "火",
    8: "金", 9: "金",
    11: "水", 12: "水",
    4: "土", 7: "土", 10: "土", 1: "土",
}

def cast_by_time(now: datetime, profile: str = 'classical', leap_policy: str | None = None) -> dict:
    numbers = time_numbers(now, profile, leap_policy)
    return {'method': 'time', 'now_iso': now.isoformat(),
            'ymd': [now.year, now.month, now.day], 'shichen': numbers['hour_number'],
            **numbers, 'upper_tri': XIANTIAN_NUM_TO_TRIGRAM[numbers['upper_num']],
            'lower_tri': XIANTIAN_NUM_TO_TRIGRAM[numbers['lower_num']]}

def cast_by_numbers(upper: int, lower: int) -> dict:
    upper_n = ((upper - 1) % 8) + 1
    lower_n = ((lower - 1) % 8) + 1
    total = upper + lower
    change = ((total - 1) % 6) + 1
    return {
        "method": "numbers",
        "upper_num": upper_n, "lower_num": lower_n, "change_num": change,
        "input_total": total,
        "upper_tri": XIANTIAN_NUM_TO_TRIGRAM[upper_n],
        "lower_tri": XIANTIAN_NUM_TO_TRIGRAM[lower_n],
    }

def hex_info(lines: list[int], assets: dict[int, dict]) -> dict:
    upper_bin, lower_bin = lines_to_trigrams(lines)
    num, name = hex_lookup_by_trigrams(upper_bin, lower_bin)
    a = assets.get(num, {})
    return {
        "number": num, "name": name,
        "upper_trigram": BINARY_TO_TRIGRAM.get(upper_bin),
        "lower_trigram": BINARY_TO_TRIGRAM.get(lower_bin),
        "lines": [{"position": i + 1, "value": v, "visual": line_visual(v)}
                  for i, v in enumerate(lines)],
        "judgment": a.get("judgment", "(暂无)"),
    }

EPILOG = """Top-level JSON keys on stdout (UTF-8):
  method now_iso ymd shichen upper_num lower_num change_num upper_tri
  lower_tri question raw_lines changing_line main_hex changed_hex
  nuclear_hex ti_yong summary

On error: {"error": ..., "message": ...} and exit 1."""
