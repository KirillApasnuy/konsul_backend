from services.court_search_service import CourtSearchService
from services.legal_analysis_service import LegalAnalysisService
from clients.gemini_client import GeminiClient
from repositories.court_decision_repository import CourtDecisionRepository
from elasticsearch import Elasticsearch

from settings import Settings


def get_search_service():
    es = Elasticsearch(Settings.ES_HOST)
    repo = CourtDecisionRepository(es, Settings.ES_INDEX)
    return CourtSearchService(repo)

def get_analysis_service():
    return LegalAnalysisService(
        search_service=get_search_service(),
        llm_client=GeminiClient(Settings.GEMINI_API_KEY, Settings.GEMINI_MODEL)
    )
