import json
import subprocess
from eastern.meihua import from_counts, package


def _cli(*args):
    p = subprocess.run(['bin/prophet','meihua',*args], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.loads(p.stdout)


def test_meihua_classic_guanmei():
    # 梅花易數卷一「觀梅占」：辰年十二月十七日申時；34/43，革初爻动。
    # https://zh.wikisource.org/wiki/梅花易數/卷一
    r = from_counts(5,12,17,9)
    assert (r['upper_trigram'],r['lower_trigram'],r['changing_line']) == ('兑','离',1)
    assert r['main_hex']['name'] == '泽火革'
    assert r['changed_hex']['name'] == '泽山咸'
    assert r['ti_yong']['body_trigram'] == '兑'


def test_meihua_cli_numbers_random_and_range():
    assert _cli('numbers','34','43')['main_hex']['name'] == '泽火革'
    a = _cli('random','--seed','1982','--question','meihua-regression-1982','--no-record')
    b = _cli('random','--seed','1982','--question','meihua-regression-1982','--no-record')
    assert a['raw_lines'] == b['raw_lines'] and a['seed'] == 1982
    r = _cli('time','--person','S02')
    assert len(r['branches']) == 2 and r['invariants']['随时间变化']['changing_line']


def test_meihua_time_matches_classic_calendar():
    # 2000-01-23 = 己卯年十二月十七，15:00申时；年卯4。
    r = _cli('time','--datetime','2000-01-23T15:00')
    assert r['operands']['month_number'] == 12 and r['operands']['day_number'] == 17
    assert r['raw_lines'] == from_counts(4,12,17,9)['raw_lines']


def test_meihua_random_record_replay():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from functools import partial
    from core.draws import draw_once
    from cli import build_parser
    import eastern.meihua as mod
    parser, _ = build_parser()
    args = parser.parse_args(['meihua','random','--seed','371','--question','isolated meihua'])
    with TemporaryDirectory() as tmp:
        path = Path(tmp)/'draws.jsonl'
        with patch.object(mod, 'draw_once', partial(draw_once, path=path)):
            a = mod.run(args); args.seed = None; b = mod.run(args)
        assert a['raw_lines'] == b['raw_lines'] and b['draw']['reused']
        assert len(path.read_text().splitlines()) == 1
