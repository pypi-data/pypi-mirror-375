# Entry point for the codeas_mcp server.
# The server uses a simple JSON-over-stdio protocol:
# Client -> server: one JSON object per line:
#   { "id": "<id>", "tool": "ollama.chat", "input": {...} }
# Server -> client progress:
#   { "id":"<id>", "type":"progress", "payload": {...} }
# Server -> client result:
#   { "id":"<id>", "type":"result", "payload": {...} }

import sys, os, json, asyncio
from utils.logger import HistoryLogger
from tools.ollama import OllamaClient
from tools.files import FileTools
from tools.shell import ShellTool

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://127.0.0.1:11434')
CODEAS_ROOT = os.environ.get('CODEAS_ROOT', os.getcwd())
HISTORY_DIR = os.path.join(CODEAS_ROOT, '.codeas-history')

logger = HistoryLogger(HISTORY_DIR)
ollama = OllamaClient(base_url=OLLAMA_URL, logger=logger)
files = FileTools(root=CODEAS_ROOT, backup_dir='.codeas_backups', logger=logger)
shell = ShellTool(logger=logger)

TOOLS = {
    'ollama.chat': ollama.chat,
    'fs.list': files.list_dir,
    'fs.read': files.read_file,
    'fs.write': files.write_file,
    'fs.edit': files.edit_file,
    'fs.delete': files.delete_path,
    'shell.run': shell.run_cmd
}

async def handle_call(msg):
    id_ = msg.get('id')
    tool = msg.get('tool')
    inp = msg.get('input', {})
    if tool not in TOOLS:
        out = {'id': id_, 'type': 'result', 'error': f'Unknown tool: {tool}'}
        print(json.dumps(out), flush=True)
        return
    try:
        func = TOOLS[tool]
        # All tool functions return an awaitable (coroutine) which may call progress_cb as they run.
        result_coro = func(inp, progress_cb=lambda p: progress(id_, p))
        if asyncio.iscoroutine(result_coro):
            res = await result_coro
        else:
            res = result_coro
        out = {'id': id_, 'type': 'result', 'payload': res}
        print(json.dumps(out), flush=True)
    except Exception as e:
        out = {'id': id_, 'type': 'result', 'error': str(e)}
        print(json.dumps(out), flush=True)

def progress(id_, payload):
    msg = {'id': id_, 'type': 'progress', 'payload': payload}
    print(json.dumps(msg), flush=True)
    try:
        logger.append('progress', {'id': id_, 'payload': payload})
    except Exception:
        pass

async def repl():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    while True:
        line = await reader.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue
        try:
            text = line.decode().strip()
        except:
            text = line.strip()
        if not text:
            continue
        try:
            msg = json.loads(text)
        except Exception:
            err = {'type': 'error', 'error': 'invalid json', 'raw': text}
            print(json.dumps(err), flush=True)
            continue
        asyncio.create_task(handle_call(msg))

def main():
    print(json.dumps({'type':'ready', 'message':'codeas_mcp ready'}), flush=True)
    try:
        asyncio.run(repl())
    except KeyboardInterrupt:
        print(json.dumps({'type':'exit', 'message':'shutting down'}), flush=True)

if __name__ == '__main__':
    main()
