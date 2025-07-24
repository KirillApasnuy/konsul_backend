from http.client import HTTPException
from typing import Dict, Any

from elastic_transport import ObjectApiResponse
from fastapi import APIRouter, Depends

from api.models.request.legal_analysis_request import LegalAnalysisRequest
from api.models.request.legal_search_request import LegalSearchRequest
from api.models.response.base_response import BaseResponse
from core.dependencies import get_analysis_service, get_search_service
from services.court_search_service import CourtSearchService
from services.legal_analysis_service import LegalAnalysisService

router = APIRouter(
    prefix="/search",
    tags=["search/analys legal-cases"])


@router.post("/legal-analysis", response_model=BaseResponse)
async def analyze_legal_practice(
        request: LegalAnalysisRequest,
        analysis_service: LegalAnalysisService = Depends(get_analysis_service)
):
    """
    Анализ судебной практики с помощью Gemini
    """
    try:
        result = await analysis_service.analyze(request)
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@router.post("/legal-cases", response_model=BaseResponse)
async def search_legal_cases(
        request: LegalSearchRequest,
        search_service: CourtSearchService = Depends(get_search_service)
):
    """
    Поиск релевантных дел
    """
    try:
        result = await search_service.smart_search(request)
        return BaseResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


