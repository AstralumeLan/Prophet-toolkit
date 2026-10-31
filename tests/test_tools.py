"""Discovery and output contracts use fictional examples, with no external validator."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys

from cli import build_parser, main
from core.schema_check import validate
from core.tools import arguments, commands, manifest

ROOT = Path(__file__).resolve().parents[1]


def test_tools_manifest_complete():
    parser, errors = build_parser()
    assert not errors, errors
    tools = manifest(parser)['tools']
    expected = {'.'.join(path) for path, _, _, _ in commands(parser)}
    assert {t['name'] for t in tools} == expected
    assert len(tools) == len(expected)
    for t in tools:
        schema = json.loads((ROOT / t['output_schema']).read_text())
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        assert t['parameters']['type'] == 'object'
    with contextlib.redirect_stdout(io.StringIO()) as output:
        assert main(['--describe']) == 0
    assert json.loads(output.getvalue()) == manifest()


def test_tools_sample_outputs_validate():
    # Resolve uses both exact and approximate fictional inputs; arrays are also outputs.
    examples = [('bazi.chart', {'person': 'S01'}), ('person.resolve', {'person': 'S02'}),
                ('tarot.card', {'name': 'The Fool'}), ('bazi.daily', {'person': 'S01', 'date': '2026-10-31'})]
    for name, values in examples:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            assert main(arguments(name, values)) == 0
        schema = json.loads((ROOT / 'schemas' / (name + '.schema.json')).read_text())
        validate(json.loads(output.getvalue()), schema)


def test_tools_parameter_conversion():
    argv = arguments('bazi.chart', {'person': 'S01', 'sect': 1, 'save_cache': False, 'pretty': True})
    assert '--pretty' in argv and '--save-cache' not in argv
    assert arguments('selftest', {'pattern': 'example'}) == ['selftest', '-k', 'example']
    for values in ({'sect': 9}, {'lat': True}, {'unknown': 'x'}):
        try: arguments('bazi.chart', values)
        except (ValueError, AssertionError): pass
        else: raise AssertionError('Invalid argument accepted')


def test_selftest_failure_exit_status():
    # Exercise CLI status propagation with a synthetic failing selftest result.
    code = "import tests.selftest as t; t.run=lambda pattern: {'selftest': {'failed': 1}, '_exit_code': 1}; from cli import main; raise SystemExit(main(['selftest']))"
    p = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 1
    assert json.loads(p.stdout)['selftest']['failed'] == 1
