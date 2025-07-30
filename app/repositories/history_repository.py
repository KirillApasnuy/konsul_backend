import json
from pathlib import Path

from models.history_entry import HistoryEntry


class HistoryRepository:
    def __init__(self, file_path: str = ".\logs\history.log"):
        self.file = Path(file_path)

    def save(self, entry: HistoryEntry):
        with self.file.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")
