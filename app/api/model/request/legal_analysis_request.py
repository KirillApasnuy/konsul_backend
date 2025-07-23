from typing import Optional

from pydantic import BaseModel


class LegalAnalysisRequest(BaseModel):
    query: str
    limit: Optional[int] = 15