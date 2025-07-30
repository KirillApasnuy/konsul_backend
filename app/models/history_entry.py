from pydantic import BaseModel
from datetime import datetime

class HistoryEntry(BaseModel):
    user_query: str
    legal_query: str
    duration: float
    timestamp: datetime
