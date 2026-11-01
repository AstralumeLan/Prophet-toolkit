"""Offline behavioral checks using explicit fictional input and synthetic evidence."""
import json
from pathlib import Path
import subprocess
import tempfile

from core.evidence import resolve_path, check_bundle
from core.cross_check import compare, run

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    chart = {'engine': {'name': 'eastern.bazi', 'version': 'test', 'rules': {}},
             'warnings': [], 'candidates': [{'day_master': '己', 'optional': None}]}
    item = {'claim': '日主为己', 'system': 'bazi', 'json_paths': ['$.candidates[0].day_master'],
            'school': '事实', 'rule_id': 'bazi.day-master.fact', 'corpus_reference': {'query': '日主'},
            'confidence': 'high', 'counter_interpretation': '日主不足以判旺衰'}
    return {'chart': chart, 'evidence': [item]}


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('Expected ValueError')


def test_json_path_resolution():
    chart = {'中文.键': [{'x': None}], 'a': {'b': 4}}
    assert resolve_path(chart, '$["中文.键"][0].x') is None
    assert resolve_path(chart, '$.a.b') == 4
    assert resolve_path(chart, '$') is chart


def test_json_path_missing_and_unsupported():
    chart = {'items': [1], 'x': 2}
    for path in ('items', '$.missing', '$.items[1]', '$.items[-1]', '$.items[*]', '$..x', '$.items[?(@.x)]', '$.x[0]', '$.items[00]', '$.items.x'):
        rejects(lambda: resolve_path(chart, path))


def test_evidence_valid_and_null():
    bundle = fixture()
    assert check_bundle(bundle)['valid']
    bundle['evidence'][0]['json_paths'] = ['$.candidates[0].optional']
    assert check_bundle(bundle)['valid']  # Existence, not semantic support.


def test_evidence_invalid_fields():
    for key, value in [('system', 'ziwei'), ('confidence', 0.9), ('json_paths', []),
                       ('json_paths', ['$']), ('json_paths', ['$.made_up']),
                       ('corpus_reference', {}), ('corpus_reference', {'id': ' '}),
                       ('claim', ''), ('school', None), ('rule_id', ''), ('counter_interpretation', '')]:
        bundle = fixture(); bundle['evidence'][0][key] = value
        assert not check_bundle(bundle)['valid'], (key, value)
    bundle = fixture(); bundle['evidence'][0]['extra'] = 1
    assert not check_bundle(bundle)['valid']


def test_evidence_envelope_and_engine():
    for bundle in ({}, {'chart': {}, 'evidence': []}, [], {'chart': {}, 'evidence': 'bad'}):
        rejects(lambda: check_bundle(bundle))
    bundle = fixture(); bundle['chart'] = {}
    assert not check_bundle(bundle)['valid']


def test_evidence_cli_exit_status():
    with tempfile.TemporaryDirectory() as directory:
        file = Path(directory) / 'evidence.json'
        for valid in (True, False):
            bundle = fixture()
            if not valid: bundle['evidence'][0]['json_paths'] = ['$.missing']
            file.write_text(json.dumps(bundle, ensure_ascii=False), encoding='utf-8')
            p = subprocess.run([str(ROOT / 'bin/prophet'), 'evidence', 'check', str(file)], capture_output=True, text=True)
            assert p.returncode == (0 if valid else 1), p.stderr
            assert json.loads(p.stdout)['valid'] == valid


def cross_args(systems='bazi,ziwei', interval=False):
    from cli import build_parser
    parser, errors = build_parser()
    assert not errors, errors
    argv = ['cross-check', 'run', '--date', '1990-03-14', '--lat', '39.9', '--lon', '116.4', '--tz', 'Asia/Shanghai', '--gender', 'male', '--systems', systems]
    argv += ['--time-range', '20:00-21:00'] if interval else ['--time', '08:15']
    return parser.parse_args(argv)


def test_cross_check_comparison_categories():
    def summary(facts):
        return {'facts': {k: [{'value': v, 'json_path': '$.fact'}] for k, v in facts.items()}}
    result = compare({'a': summary({'same': 1, 'different': 1, 'only': 3}), 'b': summary({'same': 1, 'different': 2})})
    assert [x['topic'] for x in result['agreements']] == ['same']
    assert [x['topic'] for x in result['conflicts']] == ['different']
    assert [x['topic'] for x in result['unique']] == ['only']


def test_cross_check_independent_charts_and_paths():
    args = cross_args('bazi,ziwei,western'); args.include_charts = True
    result = run(args)
    assert set(result['summaries']) == {'bazi', 'ziwei', 'western'}
    for system, summary in result['summaries'].items():
        assert summary['branch_count'] >= 1
        for facts in summary['facts'].values():
            for fact in facts:
                raw = resolve_path(result['charts'][system], fact['json_path'])
                assert fact['value'] in raw.split() if 'transform' in fact else raw == fact['value']
    assert result['comparison']['agreements']


def test_cross_check_interval_and_compact():
    result = run(cross_args(interval=True))
    assert 'charts' not in result
    assert result['input']['time'] is None
    assert result['input']['time_range'] == ['20:00', '21:00']
    assert all(s['branch_count'] >= 2 and s['invariants'] for s in result['summaries'].values())


def test_cross_check_invalid_selection():
    for systems in ('bazi', 'bazi,bazi', 'bazi,missing'):
        rejects(lambda: run(cross_args(systems)))


def test_skills_references_and_contract_paths():
    # Check discoverability and actual field references, rather than particular prose.
    args = cross_args(); args.include_charts = True
    charts = run(args)['charts']
    import re
    for name in ('bazi', 'ziwei', 'cross-check'):
        file = ROOT / 'skills' / name / 'SKILL.md'
        text = file.read_text(encoding='utf-8')
        front = text.split('---', 2)[1]
        assert 'name: ' + name in front and 'description:' in front
        for target in re.findall(r'\]\(([^)]+)\)', text):
            assert (file.parent / target).resolve().is_file(), target
        reference = file.parent / 'references' / 'analysis.md'
        if name in charts:
            for path in re.findall(r'`(\$[^`]+)`', reference.read_text(encoding='utf-8')):
                if path in ('$.branches[0]', '$.invariants') and name == 'ziwei': continue
                if '.liunian' in path or path in ('$.flows', '$.target.date'): continue
                resolve_path(charts[name], path.replace('[i]', '[0]'))
    schema = json.loads((ROOT / 'schemas/evidence-item.schema.json').read_text())
    assert set(schema['required']) == set(fixture()['evidence'][0])
