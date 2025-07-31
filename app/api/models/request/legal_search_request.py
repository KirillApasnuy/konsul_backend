from typing import Optional, Dict

from pydantic import BaseModel

from api.models.request.base_request import BaseRequest


class LegalSearchRequest(BaseRequest):
    filters: Optional[Dict] = None
    from_: Optional[int] = 0