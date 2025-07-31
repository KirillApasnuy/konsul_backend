from datetime import datetime

from models.history_entry import HistoryEntry
from repositories.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, repo: HistoryRepository):
        self.repo = repo

    def record(self, user_query: str, legal_query: str, duration: float):
        entry = HistoryEntry(
            user_query=user_query,
            legal_query=legal_query,
            duration=duration,
            timestamp=datetime.now()
        )
        self.repo.save(entry)
