#!/usr/bin/env python3
"""Infer permissive stable output contracts from fictional S01/S02, explicit fictional inputs, and public corpus.

No output values are retained. All persistence is redirected to temporary storage.
Requires installed optional engines and pinned local vendor sources, never network.
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def infer(value, depth=0):
    if value is None: return {'type': 'null'}
    if isinstance(value, bool): return {'type': 'boolean'}
    if isinstance(value, int): return {'type': 'integer'}
    if isinstance(value, float): return {'type': 'number'}
    if isinstance(value, str): return {'type': 'string'}
    if isinstance(value, list): return {'type': 'array', 'items': {}}
    if isinstance(value, dict):
        result = {'type': 'object', 'additionalProperties': True}
        if depth == 0:
            result.update(properties={k: infer(v, 1) for k, v in value.items()}, required=sorted(value))
            if 'engine' in value:
                result['properties']['engine'] = {'type': 'object', 'additionalProperties': True,
                    'required': ['name', 'version', 'rules'], 'properties': {
                        'name': {'type': 'string'}, 'version': {'type': 'string'},
                        'rules': infer(value['engine']['rules'], 1)}}
        return result
    raise TypeError(type(value))


def generate():
    # Override imported module state as well as function defaults; don't read private records.
    import core.inputs as inputs
    import core.draws as draws
    import core.cache as cache
    import corpus.build as build
    import corpus.search as search
    from cli import build_parser
    from core.tools import commands
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        inputs.PEOPLE = inputs.PEOPLE_EXAMPLE
        cache.CACHE = tmp / 'cache'
        draws.DRAWS = tmp / 'draws.jsonl'
        for fn in (draws.find, draws.record, draws.draw_once):
            defaults = list(fn.__defaults__)
            defaults = [draws.DRAWS if isinstance(x, Path) else x for x in defaults]
            fn.__defaults__ = tuple(defaults)
        build.DATA = tmp / 'data'; build.DATA.mkdir()
        build.INDEX = tmp / 'index.sqlite'
        for name in ('nakshatra.jsonl', 'parashara.jsonl'):
            shutil.copyfile(ROOT / 'corpus/data' / name, build.DATA / name)
        search.DATA = build.DATA
        build.build_index.__defaults__ = (build.INDEX,)
        search.search.__defaults__ = (None, 5, build.INDEX)
        search.books.__defaults__ = (build.INDEX,)
        search.get_passage.__defaults__ = (build.INDEX,)
        build.build(False)
        parser, errors = build_parser()
        if errors: raise RuntimeError(errors)
        for path, _, actions, _ in commands(parser):
            name = '.'.join(path)
            samples = []
            for person in ('S01', 'S02', None):
                argv = list(path)
                values = {'person': person, 'year': 2026, 'at': '2026-10-31', 'other': 'S01',
                          'code': person or 'S01', 'A': 3, 'B': 5, 'lines': '777777', 'question': 'Fictional schema demonstration',
                          'seed': 42, 'no_record': True, 'name': 'The Fool', 'query': '用神',
                          'passage_id': 'ziping:c001:p0001', 'pattern': 'test_bazi_daily'}
                if person is None:
                    values.update(date='2000-01-15', time='12:00', lat=39.9, lon=116.4, tz='Asia/Shanghai', gender='female', birth_date='2000-01-15')
                if name == 'geo' and person is not None: values['place'] = '北京'
                if name in ('bazi.daily', 'ziwei.horoscope'): values['date'] = '2026-10-31'
                for a in actions:
                    if a.dest not in values or values[a.dest] is None: continue
                    v = values[a.dest]
                    if a.option_strings:
                        argv.append(a.option_strings[0])
                        if a.nargs != 0: argv.append(str(v))
                    else: argv.append(str(v))
                a = parser.parse_args(argv)
                with contextlib.redirect_stderr(io.StringIO()): result = a.func(a)
                if isinstance(result, dict):
                    assert result.pop('_exit_code', 0) == 0, name
                # Normalise datetime values exactly as the JSON CLI does.
                samples.append(json.loads(json.dumps(result, default=str)))
            schema = infer(samples[0])
            if isinstance(samples[0], dict):
                schema['required'] = sorted(set.intersection(*(set(x) for x in samples)))
                for sample in samples[1:]:
                    for k, spec in infer(sample)['properties'].items():
                        schema['properties'].setdefault(k, spec)
                for k, spec in schema['properties'].items():
                    types = {infer(x[k], 1)['type'] for x in samples if k in x}
                    if len(types) > 1: spec['type'] = sorted(types)
            from core.schema_check import validate
            for sample in samples: validate(sample, schema)
            schema.update({'$schema': 'https://json-schema.org/draft/2020-12/schema',
                           'title': name + ' output',
                           '$comment': 'Generated from fictional S01/S02, explicit fictional inputs or documented public inputs by scripts/gen_schemas.py; values are not stored. Nested structures remain extensible.'})
            (ROOT / 'schemas' / (name + '.schema.json')).write_text(json.dumps(schema, ensure_ascii=False, indent=2) + '\n')
            print(name)


if __name__ == '__main__': generate()
