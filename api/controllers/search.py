from fastapi import APIRouter, Query, Depends
from typing import List

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
@router.get("/search-ss", response_model=List[dict])
async def search_documents(
    query: str = Query(..., min_length=2),
    limit: int = 10,
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_documents_ss(query, limit)

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
