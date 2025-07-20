from typing import Optional, Dict

from pydantic import BaseModel


class LegalSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict] = None
    limit: Optional[int] = 15
    from_: Optional[int] = 0