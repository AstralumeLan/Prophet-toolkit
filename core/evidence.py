"""Offline evidence contracts and a deliberately small, non-executable JSONPath subset."""
from __future__ import annotations
import json
import re
from pathlib import Path

SYSTEMS = ('bazi', 'ziwei', 'western', 'vedic', 'liuyao', 'meihua', 'qimen', 'huangli', 'tarot')
TOKEN = re.compile(r'\.([A-Za-z_\u0080-\uffff][\w\u0080-\uffff-]*)|\[(0|[1-9][0-9]*)\]|\[("(?:[^"\\]|\\.)*")\]')


def resolve_path(chart, path):
    """Resolve $ + dot keys, nonnegative indices, or JSON double-quoted keys.

    Wildcards, filters, recursive descent, negative indices and expressions are rejected.
    A present null is a valid resolved value; a missing key is never treated as null.
    """
    if not isinstance(path, str) or not path.startswith('$'):
        raise ValueError('Path must start with $')
    pos, value = 1, chart
    while pos < len(path):
        match = TOKEN.match(path, pos)
        if not match:
            raise ValueError('Unsupported path syntax: ' + path)
        key, index, quoted = match.groups()
        if index is not None:
            if not isinstance(value, list):
                raise ValueError('Index requires array: ' + path)
            try:
                value = value[int(index)]
            except IndexError as exc:
                raise ValueError('Index out of range: ' + path) from exc
        else:
            key = json.loads(quoted) if quoted else key
            if not isinstance(value, dict) or key not in value:
                raise ValueError('Missing key: ' + path)
            value = value[key]
        pos = match.end()
    return value


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def check_item(item, chart):
    errors, resolved = [], []
    required = {'claim', 'system', 'json_paths', 'rule_id', 'school', 'corpus_reference', 'confidence', 'counter_interpretation'}
    if not isinstance(item, dict):
        return {'valid': False, 'errors': ['Evidence item must be an object'], 'resolved': []}
    if set(item) != required:
        errors.append('Expected exactly fields: ' + ', '.join(sorted(required)))
    for key in ('claim', 'rule_id', 'school', 'counter_interpretation'):
        if not _text(item.get(key)):
            errors.append(key + ' must be nonblank text')
    system = item.get('system')
    if system not in SYSTEMS:
        errors.append('Unsupported system')
    engine = chart.get('engine') if isinstance(chart, dict) else None
    if not isinstance(engine, dict) or not all(k in engine for k in ('name', 'version', 'rules')):
        errors.append('Chart requires engine name/version/rules')
    elif not isinstance(system, str) or system not in str(engine['name']).lower():
        errors.append('Evidence system does not match chart engine')
    if not isinstance(chart, dict) or not isinstance(chart.get('warnings'), list):
        errors.append('Chart requires warnings array')
    if item.get('confidence') not in ('low', 'medium', 'high'):
        errors.append('confidence must be low, medium or high (qualitative, not probability)')
    ref = item.get('corpus_reference')
    if not isinstance(ref, dict) or set(ref) - {'id', 'query'} or not ref or not all(_text(v) for v in ref.values()):
        errors.append('corpus_reference requires nonblank id and/or query')
    paths = item.get('json_paths')
    if not isinstance(paths, list) or not paths:
        errors.append('json_paths must be a nonempty array')
    else:
        for path in paths:
            try:
                value = resolve_path(chart, path)
                if path == '$':
                    raise ValueError('Reference a specific chart field, not the whole chart')
                resolved.append({'path': path, 'value': value})
            except (ValueError, TypeError) as exc:
                errors.append(str(exc))
    return {'valid': not errors, 'errors': errors, 'resolved': resolved}


def check_bundle(bundle):
    """Validate {chart: raw CLI JSON, evidence: [item, ...]}; never rewrite inputs."""
    if not isinstance(bundle, dict) or set(bundle) != {'chart', 'evidence'}:
        raise ValueError('Expected exactly chart and evidence fields')
    if not isinstance(bundle['evidence'], list) or not bundle['evidence']:
        raise ValueError('evidence must be a nonempty array')
    results = [dict(index=i, **check_item(item, bundle['chart'])) for i, item in enumerate(bundle['evidence'])]
    return {'engine': {'name': 'core.evidence', 'version': '0.2.0', 'rules': {'paths': 'restricted JSONPath; no wildcards or evaluation'}},
            'warnings': ['Checks structure and field existence only; does not verify claim meaning, corpus authenticity or rule applicability.'],
            'valid': all(r['valid'] for r in results), 'items': results}


def register(subparsers):
    p = subparsers.add_parser('evidence', help='Check evidence against embedded raw chart JSON')
    q = p.add_subparsers(dest='evidence_command', required=True).add_parser('check')
    q.add_argument('file', help='Local JSON object containing chart and evidence')

    def run(args):
        result = check_bundle(json.loads(Path(args.file).read_text(encoding='utf-8')))
        return dict(result, _exit_code=0 if result['valid'] else 1)
    q.set_defaults(func=run)
