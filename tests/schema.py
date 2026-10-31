"""Frozen key lists computed once from fictional S01, checked for public engine metadata.
No private cache or source birth records are stored in these schema fixtures.
"""
import json
from pathlib import Path


def schema(name):
    return json.loads((Path(__file__).parent/'fixtures/schema_s01.json').read_text())[name]


def check_schema(out, name):
    frozen = schema(name)
    assert set(out) >= set(frozen['top'])
    assert sorted(out['engine']) == frozen['engine']
    assert sorted(out['engine']['rules']) == frozen['rules']
