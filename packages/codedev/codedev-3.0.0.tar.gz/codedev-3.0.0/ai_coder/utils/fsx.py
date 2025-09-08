import os, pathlib, shutil
from datetime import datetime

def ensure_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def resolve_path_safe(root, target):
    root = pathlib.Path(root).resolve()
    p = (root / target).resolve()
    if not str(p).startswith(str(root)):
        raise ValueError('Path escapes root')
    return p

def backup_file(backup_dir, file_path):
    try:
        ensure_dir(backup_dir)
        stamp = datetime.utcnow().isoformat().replace(':','-').replace('.','-')
        rel = pathlib.Path(file_path).name
        dst = pathlib.Path(backup_dir) / f"{stamp}__{rel}"
        shutil.copy2(file_path, dst)
    except FileNotFoundError:
        pass
