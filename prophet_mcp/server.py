"""Newline-delimited JSON-RPC MCP transport. Stdout contains protocol messages only."""
import json
from pathlib import Path
import subprocess
import sys

from core.tools import manifest, arguments
ROOT = Path(__file__).resolve().parent.parent


class InvalidRequest(ValueError):
    pass


def dispatch(method, params):
    if method == 'initialize':
        return {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}},
                'serverInfo': {'name': 'prophet', 'version': '0.2.0'}}
    if method == 'ping': return {}
    entries = manifest()['tools']
    mapping = {t['name'].replace('.', '_').replace('-', '_'): t for t in entries}
    if method == 'tools/list':
        return {'tools': [{'name': n, 'description': t['description'], 'inputSchema': t['parameters']} for n, t in mapping.items()]}
    if method == 'tools/call':
        try:
            t = mapping[params['name']]
            argv = arguments(t['name'], params.get('arguments', {}))
            # Invoke the ordinary CLI so draws keep its reuse, recording and redraw policy.
            proc = subprocess.run([sys.executable, str(ROOT / 'cli.py'), *argv], cwd=ROOT,
                                  capture_output=True, text=True)
            return {'content': [{'type': 'text', 'text': proc.stdout.strip() or proc.stderr.strip()}], 'isError': proc.returncode != 0}
        except (KeyError, ValueError, AssertionError, TypeError) as exc:
            return {'content': [{'type': 'text', 'text': str(exc) or 'Invalid arguments'}], 'isError': True}
    raise LookupError('Method not found')


def main():
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or request.get('jsonrpc') != '2.0' or not isinstance(request.get('method'), str):
                raise InvalidRequest('Invalid request')
            if 'id' not in request: continue
            params = request.get('params', {})
            if not isinstance(params, dict): raise ValueError('Params must be an object')
            result = dispatch(request['method'], params)
            response = {'jsonrpc': '2.0', 'id': request['id'], 'result': result}
        except Exception as exc:
            if isinstance(exc, json.JSONDecodeError): code = -32700
            elif isinstance(exc, InvalidRequest): code = -32600
            elif isinstance(exc, LookupError): code = -32601
            elif isinstance(exc, (ValueError, TypeError)): code = -32602
            else: code = -32603
            response = {'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request, dict) else None,
                        'error': {'code': code, 'message': str(exc)}}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
