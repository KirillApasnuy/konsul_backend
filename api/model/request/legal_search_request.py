from typing import Optional

from pydantic import BaseModel


class LegalSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 15