from http.client import HTTPException

from fastapi import APIRouter, Depends

from api.model.request.legal_analysis_request import LegalAnalysisRequest
from api.model.request.legal_search_request import LegalSearchRequest
from core.dependencies import get_analysis_service, get_search_service
from services.court_search_service import CourtSearchService
from services.legal_analysis_service import LegalAnalysisService

router = APIRouter(tags=["search/analys legal-cases"])


@router.post("/search/legal-analysis")
async def analyze_legal_practice(
        request: LegalAnalysisRequest,
        analysis_service: LegalAnalysisService = Depends(get_analysis_service)
):
    """
    Анализ судебной практики с помощью Gemini
    """
    try:
        result = await analysis_service.analyze(request)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@router.post("/search/legal-cases")
async def search_legal_cases(
        request: LegalSearchRequest,
        search_service: CourtSearchService = Depends(get_search_service)
):
    """
    Поиск релевантных дел
    """
    try:
        result = await search_service.smart_search(request)
        return {"search": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")
