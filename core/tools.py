"""Argparse is the single source of truth for CLI and MCP discovery."""
import argparse


def commands(parser, path=(), inherited=(), description=''):
    actions = tuple(a for a in parser._actions if not isinstance(a, (argparse._SubParsersAction, argparse._HelpAction, argparse._VersionAction)))
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    if subs:
        for sub in subs:
            helps = {a.dest: a.help for a in sub._choices_actions}
            for name, child in sub.choices.items():
                yield from commands(child, path + (name,), inherited + actions, helps.get(name) or description)
    elif parser.get_default('func'):
        yield path, parser, inherited + actions, description or 'Run ' + ' '.join(path)


def parameter(action):
    boolean = isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction))
    typ = 'boolean' if boolean else {int: 'integer', float: 'number'}.get(action.type, 'string')
    schema = {'type': typ}
    if action.help and action.help != argparse.SUPPRESS:
        schema['description'] = action.help
    if action.choices is not None:
        schema['enum'] = list(action.choices)
    if action.nargs in ('+', '*') or isinstance(action.nargs, int) and action.nargs > 1:
        schema = {'type': 'array', 'items': schema}
        if action.nargs == '+': schema['minItems'] = 1
        if isinstance(action.nargs, int): schema.update(minItems=action.nargs, maxItems=action.nargs)
    if action.default is not None and action.default != argparse.SUPPRESS:
        schema['default'] = action.default
    return schema


def manifest(parser=None):
    if parser is None:
        from cli import build_parser
        parser, errors = build_parser()
        if errors: raise RuntimeError(str(errors))
    tools = []
    for path, _, actions, description in commands(parser):
        properties, required = {}, []
        for a in actions:
            properties[a.dest] = parameter(a)
            if a.required or not a.option_strings and a.nargs not in ('?', '*'):
                required.append(a.dest)
        name = '.'.join(path)
        tools.append({'name': name, 'description': description,
                      'parameters': {'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False},
                      'output_schema': 'schemas/' + name + '.schema.json'})
    return {'tools': tools}


def arguments(name, values, parser=None):
    if parser is None:
        from cli import build_parser
        parser, _ = build_parser()
    entry = next((x for x in commands(parser) if '.'.join(x[0]) == name), None)
    if entry is None: raise ValueError('Unknown tool: ' + name)
    path, _, actions, _ = entry
    known = {a.dest: a for a in actions}
    if set(values) - set(known): raise ValueError('Unknown arguments')
    result = list(path)
    for a in actions:
        if a.dest not in values: continue
        value = values[a.dest]
        spec = parameter(a)
        from core.schema_check import validate
        validate(value, spec)
        if isinstance(a, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
            if value != a.default: result.append(a.option_strings[0])
        else:
            if a.option_strings: result.append(a.option_strings[0])
            result.extend(str(v) for v in (value if isinstance(value, list) else [value]))
    return result
