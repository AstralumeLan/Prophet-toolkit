"""Small type/required/enum validator for contract tests; not a full JSON Schema implementation."""
def validate(value, schema):
    typ = schema.get('type')
    types = typ if isinstance(typ, list) else [typ]
    checks = {'null': value is None, 'object': isinstance(value, dict), 'array': isinstance(value, list),
              'string': isinstance(value, str), 'boolean': isinstance(value, bool),
              'integer': isinstance(value, int) and not isinstance(value, bool),
              'number': isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert typ is None or any(checks.get(t, False) for t in types), (typ, type(value).__name__)
    if 'enum' in schema: assert value in schema['enum']
    if isinstance(value, dict):
        assert all(k in value for k in schema.get('required', []))
        for k, spec in schema.get('properties', {}).items():
            if k in value: validate(value[k], spec)
    if isinstance(value, list):
        assert len(value) >= schema.get('minItems', 0)
        assert len(value) <= schema.get('maxItems', float('inf'))
        for item in value: validate(item, schema.get('items', {}))
