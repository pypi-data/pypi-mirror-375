import os, pathlib, re
from utils.fsx import ensure_dir, resolve_path_safe, backup_file

class FileTools:
    def __init__(self, root='.', backup_dir='.codeas_backups', logger=None):
        self.root = root
        self.backup_dir = os.path.join(root, backup_dir)
        ensure_dir(self.backup_dir)
        self.logger = logger

    async def list_dir(self, input_obj, progress_cb=lambda p: None):
        dir_ = input_obj.get('dir', '.')
        absdir = resolve_path_safe(self.root, dir_)
        entries = []
        for p in pathlib.Path(absdir).iterdir():
            entries.append({'name': p.name, 'type': 'dir' if p.is_dir() else 'file'})
        return entries

    async def read_file(self, input_obj, progress_cb=lambda p: None):
        path = input_obj.get('path')
        absf = resolve_path_safe(self.root, path)
        data = pathlib.Path(absf).read_text(encoding='utf8')
        return {'path': path, 'data': data}

    async def write_file(self, input_obj, progress_cb=lambda p: None):
        path = input_obj.get('path')
        data = input_obj.get('data', '')
        absf = resolve_path_safe(self.root, path)
        ensure_dir(pathlib.Path(absf).parent)
        ensure_dir(self.backup_dir)
        backup_file(self.backup_dir, absf)
        pathlib.Path(absf).write_text(data, encoding='utf8')
        return {'ok': True, 'path': path, 'bytes': len(data)}

    async def delete_path(self, input_obj, progress_cb=lambda p: None):
        path = input_obj.get('path')
        absf = resolve_path_safe(self.root, path)
        if pathlib.Path(absf).is_dir():
            import shutil
            shutil.rmtree(absf)
        else:
            pathlib.Path(absf).unlink(missing_ok=True)
        return {'ok': True}

    async def edit_file(self, input_obj, progress_cb=lambda p: None):
        path = input_obj.get('path')
        search = input_obj.get('search', '')
        replace = input_obj.get('replace', '')
        limit = input_obj.get('limit', None)
        absf = resolve_path_safe(self.root, path)
        text = pathlib.Path(absf).read_text(encoding='utf8')
        pattern = re.escape(search)
        count = 0
        def _repl(m):
            nonlocal count, limit
            if limit and count >= limit:
                return m.group(0)
            count += 1
            return replace
        result = re.sub(pattern, _repl, text)
        ensure_dir(self.backup_dir)
        backup_file(self.backup_dir, absf)
        pathlib.Path(absf).write_text(result, encoding='utf8')
        return {'ok': True, 'replaced': count}
