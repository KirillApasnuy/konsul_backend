from typing import Optional

from openai import BaseModel


class BaseRequest(BaseModel):
    query: str
    limit: Optional[int] = 15
