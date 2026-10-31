"""Real stdio protocol smoke test, with fictional S01 only."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_stdio():
    requests = [
        {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}}},
        {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'bazi_chart', 'arguments': {'person': 'S01'}}},
        {'jsonrpc': '2.0', 'id': 4, 'method': 'ping'},
        {'jsonrpc': '2.0', 'id': 5, 'method': 'tools/call', 'params': {'name': 'bazi_chart', 'arguments': {'sect': 8}}},
        {'jsonrpc': '2.0', 'id': 6, 'method': 'missing'},
    ]
    result = subprocess.run([str(ROOT / 'bin/prophet-mcp')], cwd=ROOT,
        input=''.join(json.dumps(r) + '\n' for r in requests), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert [r['id'] for r in replies] == [1, 2, 3, 4, 5, 6]
    assert replies[0]['result']['protocolVersion'] == '2025-06-18'
    tools = replies[1]['result']['tools']
    assert any(t['name'] == 'bazi_chart' and t['inputSchema']['type'] == 'object' for t in tools)
    assert all('.' not in t['name'] for t in tools)
    call = replies[2]['result']
    assert not call['isError']
    chart = json.loads(call['content'][0]['text'])
    assert 'bazi' in chart['engine']['name'].lower() and chart['engine']['rules']
    assert replies[3]['result'] == {}
    assert replies[4]['result']['isError']
    assert replies[5]['error']['code'] == -32601


def test_mcp_protocol_errors():
    result = subprocess.run([str(ROOT / 'bin/prophet-mcp')], cwd=ROOT,
        input='not-json\n[]\n{"jsonrpc":"2.0","id":7,"method":"ping","params":[]}\n',
        capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert [r['error']['code'] for r in replies] == [-32700, -32600, -32602]
