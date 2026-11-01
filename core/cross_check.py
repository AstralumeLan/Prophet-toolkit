"""Small deterministic orchestration; chart facts stay separate from interpretation."""
from __future__ import annotations
import json
from core.evidence import resolve_path
from core.inputs import add_birth_args, resolve_birth


def compare(summaries):
    """Compare only shared semantic fact keys, retaining each system's candidate set."""
    grouped = {}
    for system, summary in summaries.items():
        for key, observations in summary['facts'].items():
            grouped.setdefault(key, {})[system] = observations
    result = {'agreements': [], 'conflicts': [], 'unique': []}
    for key, systems in grouped.items():
        values = {s: sorted({json.dumps(o['value'], ensure_ascii=False, sort_keys=True) for o in obs}) for s, obs in systems.items()}
        category = 'unique' if len(systems) == 1 else ('agreements' if len({tuple(v) for v in values.values()}) == 1 else 'conflicts')
        result[category].append({'topic': key, 'systems': systems, 'scope': 'computed candidate value sets only; no branch pairing or predictive consensus'})
    return result


def summarize(system, chart):
    facts = {}

    def add(topic, path):
        facts.setdefault(topic, []).append({'json_path': path, 'value': resolve_path(chart, path)})

    if system == 'bazi':
        for i, _ in enumerate(chart['candidates']):
            for pillar in ('year', 'month', 'day', 'hour'):
                add('calendar.' + pillar + '_pillar', f'$.candidates[{i}].{pillar}_pillar')
            add('bazi.day_master', f'$.candidates[{i}].day_master')
    elif system == 'ziwei':
        roots = [f'$.branches[{i}]' for i in range(len(chart['branches']))] if 'branches' in chart else ['$']
        for root in roots:
            path = root + '.iztro.chineseDate'
            # Iztro's representative-hour pillars are kept intact with provenance.
            words = resolve_path(chart, path).split()
            if len(words) != 4:
                raise ValueError('Unexpected iztro chineseDate format')
            for pillar, value in zip(('year', 'month', 'day', 'hour'), words):
                facts.setdefault('calendar.' + pillar + '_pillar', []).append({'json_path': path, 'value': value, 'transform': 'split whitespace: year/month/day/hour'})
            for key in ('mingGongBranch', 'shenGongBranch', 'wuxingJuName'):
                add('ziwei.' + key, root + '.renhuai.' + key)
    else:
        for i, _ in enumerate(chart['branches']):
            for name in ('Sun', 'Moon'):
                add('western.' + name + '.sign', f'$.branches[{i}].natal.planets.{name}.sign')
            add('western.ASC.sign', f'$.branches[{i}].natal.angles.ASC.sign')
    return {'engine': chart['engine'], 'warnings': chart['warnings'], 'facts': facts,
            'invariants': chart.get('invariants', {}), 'branch_count': len(chart.get('candidates', chart.get('branches', [None])))}


def run(args):
    systems = args.systems.split(',')
    if len(systems) < 2 or len(set(systems)) != len(systems) or any(s not in ('bazi', 'ziwei', 'western') for s in systems):
        raise ValueError('Choose at least two distinct systems from bazi,ziwei,western')
    birth = resolve_birth(args)
    from cli import build_parser
    parser, errors = build_parser()
    if errors:
        raise RuntimeError(str(errors))
    summaries, charts = {}, {}
    for system in systems:
        argv = [system, 'natal' if system == 'western' else 'chart']
        for key in ('person', 'date', 'time', 'time_range', 'place', 'lat', 'lon', 'tz', 'gender'):
            value = getattr(args, key, None)
            if value is not None:
                argv.extend(['--' + key.replace('_', '-'), str(value)])
        if system in ('bazi', 'ziwei'):
            argv.extend(['--time-standard', args.time_standard])
        child = parser.parse_args(argv)
        chart = child.func(child)
        charts[system] = chart
        summaries[system] = summarize(system, chart)
    result = {'engine': {'name': 'core.cross_check', 'version': '0.2.0', 'rules': {'mode': 'independent deterministic calculations; compact facts', 'time_standard': args.time_standard}},
              'warnings': ['Calendar agreement is not independent predictive evidence. Ziwei uses representative-hour pillars; boundary rules can differ.',
                           'Candidate sets are not paired across systems. Sample invariance does not guarantee continuous interval invariance.'],
              'input': birth, 'summaries': summaries, 'comparison': compare(summaries)}
    if args.include_charts:
        result['charts'] = charts
    return result


def register(subparsers):
    p = subparsers.add_parser('cross-check', help='Independent charts and compact factual comparison')
    q = p.add_subparsers(dest='cross_command', required=True).add_parser('run')
    add_birth_args(q)
    q.add_argument('--systems', default='bazi,ziwei', help='Comma-separated distinct systems: bazi,ziwei,western')
    q.add_argument('--time-standard', choices=['clock', 'true-solar'], default='clock', help='Shared eastern time standard; western always uses clock/UTC')
    q.add_argument('--include-charts', action='store_true', help='Include raw charts for evidence checking; default compact')
    q.set_defaults(func=run)
