from http.client import HTTPException

from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.responses import StreamingResponse

from api.models.request.legal_analysis_request import LegalAnalysisRequest
from api.models.request.legal_search_request import LegalSearchRequest
from api.models.response.base_response import BaseResponse
from core.dependencies import get_analysis_service, get_search_service
from services.court_search_service import CourtSearchService
from services.legal_analysis_service import LegalAnalysisService
from settings import Settings

router = APIRouter(
    prefix="/search",
    tags=["search/analys legal-cases"])


@router.post("/legal-analysis", response_model=BaseResponse)
async def analyze_legal_practice(
        request: LegalAnalysisRequest,
        background_tasks: BackgroundTasks,
        analysis_service: LegalAnalysisService = Depends(get_analysis_service)
):
    f"""
    Анализ судебной практики с помощью Gemini: {Settings.GEMINI_MODEL}
    """
    try:
        result = await analysis_service.analyze(request, background_tasks=background_tasks)
        if request.is_stream:
            return StreamingResponse(content=result, media_type="text/plain")
        else:
            return BaseResponse(data=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@router.post("/legal-cases", response_model=BaseResponse)
async def search_legal_cases(
        request: LegalSearchRequest,
        background_tasks: BackgroundTasks,
        search_service: CourtSearchService = Depends(get_search_service)
):
    """
    Поиск релевантных дел
    """
    try:
        result = await search_service.smart_search(request, background_tasks=background_tasks)
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")
