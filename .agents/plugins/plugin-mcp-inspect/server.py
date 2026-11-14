#!/usr/bin/env python3
"""Local, unauthenticated MCP fixture for new/resume launch verification."""
import json
import os
from pathlib import Path
import sys

if '--fail' in sys.argv:
    print('PLUGIN_MCP_EXPECTED_START_FAILURE', file=sys.stderr, flush=True)
    sys.exit(23)

for line in sys.stdin:
    message = json.loads(line)
    if 'id' not in message:
        continue
    method = message.get('method')
    if method == 'initialize':
        result = {
            'protocolVersion': message['params']['protocolVersion'],
            'capabilities': {'tools': {}},
            'serverInfo': {'name': 'plugin-mcp-inspect', 'version': '1.0.0'},
        }
    elif method == 'tools/list':
        result = {'tools': [{
            'name': 'inspect',
            'description': 'Return the actual working directory and bundled Plugin asset.',
            'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False},
        }]}
    elif method == 'tools/call' and message.get('params', {}).get('name') == 'inspect':
        result = {'content': [{'type': 'text', 'text': json.dumps({
            'cwd': os.getcwd(),
            'asset': Path(os.environ['PLUGIN_ASSET']).read_text().strip(),
        })}]}
    elif method == 'ping':
        result = {}
    else:
        print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'error': {
            'code': -32601, 'message': 'Method not found',
        }}), flush=True)
        continue
    print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}), flush=True)
