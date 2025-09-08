import httpx, asyncio, json
from typing import Callable

class OllamaClient:
    def __init__(self, base_url='http://127.0.0.1:11434', logger=None):
        self.base_url = base_url.rstrip('/')
        self.logger = logger

    async def _stream_chat(self, body, progress_cb: Callable[[dict], None]):
        url = f"{self.base_url}/api/chat"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream('POST', url, json=body) as resp:
                async for chunk in resp.aiter_text():
                    if not chunk:
                        continue
                    # Ollama often streams JSON lines; try to parse per-line
                    for line in chunk.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            j = json.loads(line)
                            # extract token-like content
                            token = None
                            if isinstance(j, dict):
                                token = j.get('message', {}).get('content') or j.get('response') or j.get('text')
                            if token:
                                progress_cb({'message': token})
                        except Exception:
                            # send raw chunk
                            progress_cb({'message': line})
        return

    def chat(self, input_obj, progress_cb=lambda p: None):
        # input_obj: { 'prompt': str, 'system': Optional[str], 'model': Optional[str], 'stream': bool }
        prompt = input_obj.get('prompt', '')
        system = input_obj.get('system')
        model = input_obj.get('model', 'deepseek-r1:8b')
        stream = input_obj.get('stream', True)
        body = {
            'model': model,
            'stream': True,
            'messages': []
        }
        if system:
            body['messages'].append({'role':'system','content':system})
        body['messages'].append({'role':'user','content':prompt})
        # Log prompt
        if self.logger:
            try:
                self.logger.append('prompt', {'model': model, 'prompt': prompt, 'system': system})
            except Exception:
                pass
        async def _run():
            await self._stream_chat(body, progress_cb)
            return {'ok': True}
        return _run()
