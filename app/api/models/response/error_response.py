from typing import Optional

from app.api.model.response.base_response import BaseResponse


class ErrorResponse(BaseResponse):
    error: Optional[str] = None