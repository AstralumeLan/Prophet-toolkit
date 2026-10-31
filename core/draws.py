"""随机占记录：core/draws.jsonl。问题原文、时刻、时区、方法、seed、结果。不重抽。"""
from __future__ import annotations
import json
import secrets
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DRAWS = Path(__file__).resolve().parent / "draws.jsonl"


def new_seed() -> int:
    return secrets.randbelow(2**63)


def find(method: str, question: str, seed: int | None = None, path: Path = DRAWS) -> dict | None:
    if not path.exists():
        return None
    hit = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("method") == method and r.get("question") == question and (seed is None or r.get("seed") == seed):
            hit = r
    return hit


def record(method: str, question: str, seed: int | None, result, tz: str = "Asia/Shanghai",
           extra: dict | None = None, path: Path = DRAWS, no_record: bool = False) -> dict:
    now = datetime.now(ZoneInfo(tz))
    rec = {"method": method, "question": question, "time": now.isoformat(timespec="seconds"), "tz": tz,
           "seed": seed, **(extra or {}), "result": result}
    if not no_record:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    return rec


def draw_once(method: str, question: str, seed: int | None, compute, tz: str = "Asia/Shanghai",
              extra: dict | None = None, no_record: bool = False, path: Path = DRAWS) -> dict:
    """Return the existing record for (method, question[, seed]) or compute+record a new one.

    Policy: the same question is not re-drawn. If a record exists for the same method+question,
    it is returned with `"reused": true` unless an explicit different seed is given (then a new draw is recorded
    and flagged `"redraw_warning"`).
    """
    prev = find(method, question, None, path)
    if prev and (seed is None or prev.get("seed") == seed):
        return {**prev, "reused": True, "note": "同一问题已有记录，按不重抽原则返回原结果"}
    warn = None
    if prev and seed is not None and prev.get("seed") != seed:
        warn = "同一问题已有不同 seed 的记录；这是重抽，审计时应以首次结果为准"
    seed = new_seed() if seed is None else seed
    result = compute(seed)
    rec = record(method, question, seed, result, tz, extra, path, no_record)
    out = {**rec, "reused": False}
    if warn:
        out["redraw_warning"] = warn
    return out


def register(sub):
    p = sub.add_parser("draws", help="随机占记录")
    sp = p.add_subparsers(dest="sub", required=True)
    ls = sp.add_parser("list"); ls.add_argument("--method")
    def _ls(a):
        if not DRAWS.exists():
            return {"draws": []}
        rs = [json.loads(l) for l in DRAWS.read_text(encoding="utf-8").splitlines() if l.strip()]
        return {"draws": [r for r in rs if not a.method or r.get("method") == a.method]}
    ls.set_defaults(func=_ls)
