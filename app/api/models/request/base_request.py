from typing import Optional

from pydantic import BaseModel


class BaseRequest(BaseModel):
    query: str
    limit: Optional[int] = 15
