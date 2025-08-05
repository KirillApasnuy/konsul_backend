from elasticsearch import Elasticsearch
from fastapi import BackgroundTasks

from clients.gemini_client import GeminiClient
from repositories.court_decision_repository import CourtDecisionRepository
from repositories.history_repository import HistoryRepository
from services.court_search_service import CourtSearchService
from services.history_service import HistoryService
from services.legal_analysis_service import LegalAnalysisService
from settings import Settings


def get_decision_repository():
    es = Elasticsearch(Settings.ES_HOST)
    return CourtDecisionRepository(es, Settings.ES_INDEX)

def get_history_repository():
    return HistoryRepository()

def get_gemini_client():
    return GeminiClient(Settings.GEMINI_API_KEY,
                        Settings.GEMINI_MODEL)


def get_search_service():
    return CourtSearchService(
        get_decision_repository(),
        get_gemini_client(),
        get_history_service())


def get_history_service():
    return HistoryService(get_history_repository())

def get_analysis_service():
    return LegalAnalysisService(
        search_service=get_search_service(),
        llm_client=get_gemini_client()
    )
