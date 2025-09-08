import asyncio
from asyncio.subprocess import PIPE

class ShellTool:
    def __init__(self, logger=None):
        self.logger = logger

    async def _stream_proc(self, cmd, cwd, progress_cb):
        proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd)
        async def reader(stream, kind):
            while True:
                line = await stream.readline()
                if not line:
                    break
                progress_cb({'stream': kind, 'output': line.decode('utf8', 'replace')})
        await asyncio.gather(reader(proc.stdout, 'stdout'), reader(proc.stderr, 'stderr'))
        rc = await proc.wait()
        return {'ok': rc == 0, 'code': rc}

    def run_cmd(self, input_obj, progress_cb=lambda p: None):
        cmd = input_obj.get('cmd', '')
        cwd = input_obj.get('cwd', None)
        async def _run():
            return await self._stream_proc(cmd, cwd, progress_cb)
        return _run()
