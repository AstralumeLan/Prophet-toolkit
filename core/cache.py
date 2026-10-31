"""命盘 JSON 缓存：core/cache/<人物>__<体系>__<规则版本>.json，带引擎版本号。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache"


def rules_tag(rules: dict) -> str:
    return hashlib.sha1(json.dumps(rules, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]


def path_for(person: str, system: str, rules: dict) -> Path:
    return CACHE / f"{person}__{system}__{rules_tag(rules)}.json"


def save(person: str, system: str, rules: dict, data: dict) -> str:
    CACHE.mkdir(exist_ok=True)
    p = path_for(person, system, rules)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(p)


def load(person: str, system: str, rules: dict) -> dict | None:
    p = path_for(person, system, rules)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def register(sub):
    p = sub.add_parser("cache", help="命盘缓存")
    sp = p.add_subparsers(dest="sub", required=True)
    ls = sp.add_parser("list")
    ls.set_defaults(func=lambda a: {"files": sorted(x.name for x in CACHE.glob("*.json"))})
