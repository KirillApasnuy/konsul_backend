from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


class CourtDecision(BaseModel):
    court: str
    case_number: str
    date: str
    text_of_decision: str
    URL: Optional[str]
    text_length: Optional[int]
    year: Optional[int]
    month: Optional[int]
    court_region: Optional[str]
    case_category: Optional[str]
    text_hash: Optional[str]
    created_at: Optional[datetime]


class SearchFilters(BaseModel):
    court_region: Optional[str]
    case_category: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]


class SearchResult(BaseModel):
    score: float
    source: CourtDecision
    highlight: Optional[Dict[str, List[str]]]


class SmartSearchResponse(BaseModel):
    total: int
    max_score: float
    results: List[SearchResult]
    aggregations: Optional[Dict]