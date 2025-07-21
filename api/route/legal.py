from http.client import HTTPException

from fastapi import APIRouter, Depends

from api.model.request.legal_analysis_request import LegalAnalysisRequest
from api.model.request.legal_search_request import LegalSearchRequest
from services.court_indexing_service import CourtIndexingService
from services.court_search_service import CourtSearchService
from services.legal_analysis_service import LegalAnalysisService
from core.dependencies import get_analysis_service, get_search_service, get_indexing_service

router = APIRouter()

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
async def analyze_legal_practice(
        request: LegalSearchRequest,
        search_service: CourtSearchService = Depends(get_search_service)
):
    try:
        result = await search_service.smart_search(request)
        return {"search": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@router.post("/es/create_index")
async def analyze_legal_practice(indexing_service: CourtIndexingService = Depends(get_indexing_service)):
    try:
        result = await indexing_service.create_es_index()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

