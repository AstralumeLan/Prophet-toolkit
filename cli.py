"""Prophet 统一入口：prophet <体系> <子命令> [--person Sxx | --date --time --place] ...  输出 JSON。"""
from __future__ import annotations
import argparse
import importlib
import json
import sys
import traceback

VERSION = "0.1.0"
# (module path) — each exposes register(subparsers)
MODULES = [
    "core.inputs", "core.geo", "core.solartime", "core.draws", "core.cache",
    "eastern.bazi", "eastern.ziwei", "eastern.liuyao", "eastern.meihua", "eastern.qimen", "eastern.huangli",
    "western.astro", "western.tarot",
    "vedic.jyotish",
    "corpus.search",
    "validate.cross",
    "tests.selftest",
]


def build_parser():
    ap = argparse.ArgumentParser(prog="prophet", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"prophet {VERSION}")
    ap.add_argument("--pretty", action="store_true", help="缩进输出 JSON")
    sub = ap.add_subparsers(dest="system", metavar="<体系>")
    load_errors = {}
    for m in MODULES:
        try:
            importlib.import_module(m).register(sub)
        except ModuleNotFoundError as e:
            if e.name and m.startswith(e.name):
                continue  # module not built yet
            load_errors[m] = repr(e)
        except Exception as e:  # noqa: BLE001
            load_errors[m] = repr(e)
    tools = sub.add_parser("tools", help="Discover commands and JSON input schemas")
    from core.tools import manifest
    tools.set_defaults(func=lambda a: manifest(ap))
    return ap, load_errors


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    pretty = "--pretty" in argv
    argv = [x for x in argv if x != "--pretty"]
    if argv == ["--describe"]:
        argv = ["tools"]
    ap, load_errors = build_parser()
    a = ap.parse_args(argv)
    a.pretty = pretty
    if not getattr(a, "func", None):
        ap.print_help()
        if load_errors:
            print(json.dumps({"module_load_errors": load_errors}, ensure_ascii=False), file=sys.stderr)
        return 2
    try:
        out = a.func(a)
        code = 0
        if isinstance(out, dict) and out.get("_exit_code") is not None:
            code = out.pop("_exit_code")
    except Exception as e:  # noqa: BLE001
        out = {"error": type(e).__name__, "message": str(e), "trace": traceback.format_exc().splitlines()[-6:]}
        code = 1
    try:
        print(json.dumps(out, ensure_ascii=False, indent=2 if a.pretty else None, default=str))
        sys.stdout.flush()
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return code


if __name__ == "__main__":
    sys.exit(main())
