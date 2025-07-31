import os

from fastapi import APIRouter
from starlette.responses import FileResponse

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

@router.get("/query-history")
async def get_query_history():
    return FileResponse(path="/app/logs/history.log", filename="query-history.log", media_type='multipart/form-data')