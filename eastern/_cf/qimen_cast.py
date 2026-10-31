# MIT excerpts from ShousenZHANG/chinese-fortune; see LICENSE and NOTICE.
"""MIT adaptation; provenance in NOTICE."""
from __future__ import annotations
from .qimen_tables import *
from .utils import *
from .qimen_dingju import *

def earth_plate(ju_type: str, ju_number: int) -> dict[int, str]:
    """Place 三奇六仪 across 9 palaces.

    阳遁 N 局: 戊起 N 宫, 顺布 (按 1..9 palace path) 六仪+三奇.
    阴遁 N 局: 戊起 N 宫, 逆布 (按 9..1 palace path) 六仪+三奇.

    Returns dict mapping palace_index (1..9) -> 干名.
    """
    if not (1 <= ju_number <= 9):
        raise ValueError(f"ju_number out of range: {ju_number}")

    # Build path of 9 palaces starting at ju_number, traversing in 顺/逆 direction.
    if ju_type == "阳遁":
        full_seq = YANG_PALACE_SEQ
    elif ju_type == "阴遁":
        full_seq = YIN_PALACE_SEQ
    else:
        raise ValueError(f"unknown ju_type: {ju_type}")

    start_idx = full_seq.index(ju_number)
    path = [full_seq[(start_idx + k) % 9] for k in range(9)]

    return {palace: YIQI_ORDER[k] for k, palace in enumerate(path)}

def xun_head(stem: str, branch: str) -> tuple[str, str]:
    """Return (旬首名 e.g. '甲子', 对应六仪 e.g. '戊') for 干支."""
    idx = jiazi_index(stem, branch)
    head_idx = idx - (idx % 10)  # 0,10,20,30,40,50
    return XUN_HEADS[head_idx // 10]

EIGHT_RING_YANG: list[int] = [1, 8, 3, 4, 9, 2, 7, 6]

EIGHT_RING_YIN: list[int] = [1, 6, 7, 2, 9, 4, 3, 8]

def _resolve_ring_palace(palace: int) -> int:
    """If palace == 5, fall back to 2 (寄坤). Otherwise return as-is."""
    return 2 if palace == 5 else palace

def star_plate(zhi_fu_palace: int, shi_gan_palace: int, ju_type: str) -> dict[int, str]:
    """Legacy eight-ring stars with 天禽 stored at 5; not Yuanling's method."""
    ring = EIGHT_RING_YANG if ju_type == "阳遁" else EIGHT_RING_YIN

    # Compatibility map. Actual co-location of 天禽 is not implemented here.
    home_ring: dict[int, str] = {
        1: "天蓬", 8: "天任", 3: "天冲", 4: "天辅",
        9: "天英", 2: "天芮", 7: "天柱", 6: "天心",
    }

    from_pal = _resolve_ring_palace(zhi_fu_palace)
    to_pal = _resolve_ring_palace(shi_gan_palace)
    from_idx = ring.index(from_pal)
    to_idx = ring.index(to_pal)
    shift = (to_idx - from_idx) % 8

    star_result: dict[int, str] = {}
    for k, palace in enumerate(ring):
        target = ring[(k + shift) % 8]
        star_result[target] = home_ring[palace]

    # Legacy storage: this is NOT an implemented co-location with 天芮.
    star_result[5] = "天禽"
    return star_result

def men_plate(zhi_fu_palace: int, shi_gan_palace: int, ju_type: str) -> dict[int, str]:
    """Rotate 八门. 值使门 = zhi_fu_palace's 本门; 该门飞到 时干宫.

    八门 home positions: 1坎-休门 2坤-死门 3震-伤门 4巽-杜门
                         5中-无门 6乾-开门 7兑-惊门 8艮-生门 9离-景门
    """
    ring = EIGHT_RING_YANG if ju_type == "阳遁" else EIGHT_RING_YIN
    home_ring: dict[int, str] = {
        1: "休门", 8: "生门", 3: "伤门", 4: "杜门",
        9: "景门", 2: "死门", 7: "惊门", 6: "开门",
    }

    from_pal = _resolve_ring_palace(zhi_fu_palace)
    to_pal = _resolve_ring_palace(shi_gan_palace)
    from_idx = ring.index(from_pal)
    to_idx = ring.index(to_pal)
    shift = (to_idx - from_idx) % 8

    men_result: dict[int, str] = {}
    for k, palace in enumerate(ring):
        target = ring[(k + shift) % 8]
        men_result[target] = home_ring[palace]
    # 中5 stays without 八门.
    return men_result

def shen_plate(shi_gan_palace: int, ju_type: str) -> dict[int, str]:
    """八神: 值符 起于 时干宫 (即 值符 当前所在宫位),
    阳顺/阴逆 沿 8-palace ring 排布. 中宫 5 无神.
    """
    ring = EIGHT_RING_YANG if ju_type == "阳遁" else EIGHT_RING_YIN
    start = _resolve_ring_palace(shi_gan_palace)
    start_idx = ring.index(start)

    shen_result: dict[int, str] = {}
    for k, name in enumerate(EIGHT_SHEN_ORDER):
        palace = ring[(start_idx + k) % 8]
        shen_result[palace] = name
    return shen_result

JI_MEN: set[str] = {"开门", "休门", "生门"}

SAN_XING_PAIRS: list[tuple[str, str]] = [
    ("寅", "巳"), ("巳", "申"), ("申", "寅"),  # 寅巳申 三刑
    ("丑", "戌"), ("戌", "未"), ("未", "丑"),  # 丑戌未 三刑
    ("子", "卯"),                              # 子卯相刑
    ("辰", "辰"), ("午", "午"), ("酉", "酉"), ("亥", "亥"),  # 自刑
]

SAN_XING_LOOKUP: dict[str, set[str]] = {}

MU_KU: dict[str, str] = {
    "甲": "未", "乙": "未",  # 木墓于未
    "丙": "戌", "丁": "戌",  # 火墓于戌
    "戊": "戌", "己": "戌",  # 阳土寄火墓
    "庚": "丑", "辛": "丑",  # 金墓于丑
    "壬": "辰", "癸": "辰",  # 水墓于辰
}

DIZHI_TO_PALACE: dict[str, int] = {
    "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
    "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6,
}

def build_palaces(
    earth: dict[int, str],
    heaven: dict[int, str],
    men: dict[int, str],
    star: dict[int, str],
    shen: dict[int, str],
) -> list[dict]:
    out: list[dict] = []
    for p in range(1, 10):
        info = PALACE_INFO[p]
        notes: list[str] = []
        if p == 5:
            notes.append("中宫；寄宫须按所选方法另核，不能固定称天芮天禽同宫")
        out.append({
            "index": p,
            "palace": info["palace"],
            "direction": info["direction"],
            "wuxing": info["wuxing"],
            "earth_yi_qi": earth.get(p),
            "heaven_yi_qi": heaven.get(p),
            "men": men.get(p),
            "star": star.get(p),
            "shen": shen.get(p),
            "notes": "; ".join(notes) if notes else "",
        })
    return out

EPILOG = """Top-level JSON keys on stdout (UTF-8):
  ok tool version input ganzhi jieqi san_yuan ju_type ju_number shi_gan
  shi_zhi xun_head xun_yi zhi_fu_star zhi_fu_palace zhi_fu_origin_palace
  zhi_shi_men zhi_shi_palace palaces patterns method_profile summary

On error: {"error": ..., "message": ...} and exit 1."""
