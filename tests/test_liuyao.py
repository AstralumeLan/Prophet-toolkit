"""京房纳甲公开表：chinese-fortune scripts/liuyao_cast.py NAJIA_TABLE/EIGHT_PALACES。"""
import json
import random
import subprocess
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from functools import partial
from core.draws import draw_once
from eastern.liuyao import chart
from eastern._iching import cast_coins


def _cli(*args):
    p = subprocess.run(['bin/prophet', 'liuyao', *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.loads(p.stdout)


def test_liuyao_qian_najia_and_gou_palace():
    r = chart([7]*6, datetime.fromisoformat('2026-10-31T12:00:00+08:00'))
    assert r['main_chart']['hex_name'] == '乾为天' and not r['active_lines']
    assert [l['stem']+l['branch'] for l in r['main_chart']['lines']] == ['甲子','甲寅','甲辰','壬午','壬申','壬戌']
    assert r['main_chart']['shi_position'] == 6
    g = chart([8,7,7,7,7,7], datetime.fromisoformat('2026-10-31T12:00:00+08:00'))
    assert (g['main_chart']['hex_name'], g['main_chart']['palace'], g['main_chart']['shi_position']) == ('天风姤','乾宫',1)


def test_liuyao_cli_and_seeded_coins():
    assert _cli('manual', '--lines', '777777')['main_chart']['hex_name'] == '乾为天'
    r = _cli('coins', '--seed', '90817', '--question', 'liuyao-regression-90817', '--no-record')
    assert r['raw_lines'] == cast_coins(random.Random(90817))
    assert r['raw_lines'] == _cli('coins','--seed','90817','--question','liuyao-regression-90817','--no-record')['raw_lines']


def test_liuyao_record_replay_and_range():
    from cli import build_parser
    import eastern.liuyao as mod
    parser, _ = build_parser()
    args = parser.parse_args(['liuyao','coins','--seed','918','--question','isolated replay'])
    with TemporaryDirectory() as tmp:
        path = Path(tmp)/'draws.jsonl'
        with patch.object(mod, 'draw_once', partial(draw_once, path=path)):
            a = mod.run(args); args.seed = None; b = mod.run(args)
        assert a['raw_lines'] == b['raw_lines'] and b['draw']['reused']
        assert len(path.read_text().splitlines()) == 1
    r = _cli('time','--person','S02')
    assert len(r['branches']) == 2 and 'invariants' in r


def test_liuyao_changed_relatives_and_fushen():
    r = chart([6,7,7,7,7,7], datetime.fromisoformat('2026-10-31T12:00:00+08:00'))
    assert r['active_lines'] == [1]
    assert r['changed_chart']['liu_qin_basis']['palace'] == r['main_chart']['palace']
    assert r['changed_chart']['hex_name'] == '乾为天'
    assert {l['liu_qin'] for l in r['伏神']} == {'妻财'}
