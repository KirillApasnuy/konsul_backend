from typing import Optional

from pydantic import BaseModel

from api.models.request.base_request import BaseRequest


class LegalAnalysisRequest(BaseRequest):
    is_stream: bool = False