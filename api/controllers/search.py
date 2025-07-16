from typing import List

from fastapi import APIRouter, Query, Depends, HTTPException

from api.model.request.legal_analysis_request import LegalAnalysisRequest
from api.model.request.legal_search_request import LegalSearchRequest
from core.dependencies import get_search_service
from services.search_service import SearchService

router = APIRouter()


@router.get("/search", response_model=List[dict])
async def search_documents(
        query: str = Query(..., min_length=2),
        limit: int = 10,
        search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_documents(query, limit)


@router.post("/search/legal-cases")
async def search_legal_cases(
        request: LegalSearchRequest,
        search_service: SearchService = Depends(get_search_service)
):
    """
    Поиск судебных дел с подсветкой фрагментов
    """
    try:
        results = await search_service.search_legal_cases(
            query_text=request.query,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/legal-analysis")
async def analyze_legal_practice(
        request: LegalAnalysisRequest,
        search_service: SearchService = Depends(get_search_service)
):
    """
    Анализ судебной практики с определением предмета доказывания
    """
    try:
        results = await search_service.analyze_legal_practice(
            query_text=request.query,
            limit=request.limit
        )
        return results
    except Exception as e:
        error_message = str(e)

        # Определяем тип ошибки и статус код
        if "string too long" in error_message or "string_above_max_length" in error_message:
            raise HTTPException(
                status_code=413,
                detail=f"Размер данных превышает лимит LLM сервиса. Попробуйте уменьшить количество документов или использовать более короткий запрос. Ошибка: {error_message}"
            )
        elif "invalid_request_error" in error_message:
            raise HTTPException(
                status_code=400,
                detail=f"Некорректный запрос к LLM сервису: {error_message}"
            )
        elif "Error code:" in error_message:
            raise HTTPException(
                status_code=502,
                detail=f"Ошибка внешнего LLM сервиса: {error_message}"
            )
        else:
            raise HTTPException(status_code=500, detail=error_message)


@router.get("/search/legal-cases/quick")
async def quick_legal_search(
        q: str = Query(..., description="Поисковый запрос"),
        limit: int = Query(15, ge=1, le=100, description="Количество результатов"),
        search_service: SearchService = Depends(get_search_service)  # ИСПРАВЛЕНО
):
    """
    Быстрый поиск судебных дел (GET запрос)
    """
    try:
        results = await search_service.search_legal_cases(
            query_text=q,
            limit=limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courts", response_model=List[str])
async def get_court_names(search_service: SearchService = Depends(get_search_service)):
    return await search_service.get_all_court_names()


@router.get("/categories", response_model=List[str])
async def get_categories(search_service: SearchService = Depends(get_search_service)):
    return await search_service.get_all_categories()


@router.get("/subcategories", response_model=List[str])
async def get_subcategories(
        category: str = Query(..., min_length=1),
        search_service: SearchService = Depends(get_search_service)
):
    return await search_service.get_subcategories_by_category(category)


@router.get("/search-with-summary")
async def search_with_summary(
        query: str = Query(..., min_length=2),
        limit: int = 10,
        search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_with_summary(query, limit)


@router.get("/debug/mongo-structure")
async def debug_mongo_structure(
        limit: int = Query(5, ge=1, le=20),
        search_service: SearchService = Depends(get_search_service)
):
    """
    Отладочный эндпоинт для изучения структуры данных в MongoDB
    """
    return await search_service.debug_mongo_structure(limit)
