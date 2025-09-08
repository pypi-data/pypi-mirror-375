import os, json, pathlib
from datetime import datetime

class HistoryLogger:
    def __init__(self, history_dir):
        self.history_dir = history_dir
        pathlib.Path(self.history_dir).mkdir(parents=True, exist_ok=True)

    def append(self, event, payload):
        day = datetime.utcnow().strftime('%Y-%m-%d')
        file = pathlib.Path(self.history_dir) / f"{day}.log"
        line = json.dumps({'ts': datetime.utcnow().isoformat(), 'event': event, 'payload': payload}) + '\n'
        if file.exists():
            prev = file.read_text(encoding='utf8')
            file.write_text(prev + line, encoding='utf8')
        else:
            file.write_text(line, encoding='utf8')
