"""prophet selftest：发现 tests/test_*.py 中的 test_* 函数逐个运行，输出 pass/fail JSON（stderr 打印逐项结果）。"""
from __future__ import annotations
import importlib
import sys
import time
import traceback
from pathlib import Path

TESTS = Path(__file__).resolve().parent


def run(pattern: str | None = None) -> dict:
    results = []
    for f in sorted(TESTS.glob("test_*.py")):
        mod_name = f"tests.{f.stem}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:  # noqa: BLE001
            results.append({"test": mod_name, "status": "fail", "error": f"import: {e!r}"})
            print(f"FAIL {mod_name} (import) {e!r}", file=sys.stderr)
            continue
        for name in sorted(n for n in dir(mod) if n.startswith("test_")):
            tid = f"{f.stem}::{name}"
            if pattern and pattern not in tid:
                continue
            t0 = time.time()
            try:
                getattr(mod, name)()
                st, err = "pass", None
            except Exception as e:  # noqa: BLE001
                st, err = "fail", "".join(traceback.format_exception_only(type(e), e)).strip()
                err += " @ " + traceback.format_exc().splitlines()[-3].strip()
            dt = round(time.time() - t0, 2)
            results.append({"test": tid, "status": st, "seconds": dt, **({"error": err} if err else {})})
            print(f"{'PASS' if st == 'pass' else 'FAIL'} {tid} ({dt}s){'  ' + err if err else ''}", file=sys.stderr)
    npass = sum(r["status"] == "pass" for r in results)
    summary = {"passed": npass, "failed": len(results) - npass, "total": len(results)}
    print(f"selftest: {npass}/{len(results)} passed", file=sys.stderr)
    return {"selftest": summary, "results": results, "_exit_code": 0 if npass == len(results) and results else 1}


def register(sub):
    p = sub.add_parser("selftest", help="一键运行全部回归测试")
    p.add_argument("-k", dest="pattern", help="只跑名字包含该子串的测试")
    p.set_defaults(func=lambda a: run(a.pattern))
