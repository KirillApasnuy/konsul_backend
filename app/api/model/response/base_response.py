from typing import Union, Any, Dict

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True
    data: Union[str, Dict[str, Any]]
