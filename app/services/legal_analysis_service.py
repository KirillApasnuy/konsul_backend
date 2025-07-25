from api.models.request.legal_analysis_request import LegalAnalysisRequest
from api.models.request.legal_search_request import LegalSearchRequest
from clients.gemini_client import GeminiClient
from services.court_search_service import CourtSearchService


class LegalAnalysisService:
    def __init__(self, search_service: CourtSearchService, llm_client: GeminiClient):
        self.search_service = search_service
        self.llm_client = llm_client

    async def analyze(self, request: LegalAnalysisRequest) -> str:
        search_model = LegalSearchRequest(query=request.query, limit=request.limit)

        search_result = await self.search_service.smart_search(search_model)

        if "text_of_decision" in search_result:
            return "No relevant court cases to analyze."

        texts = [hit["_source"]["text_of_decision"] + f"\nСсылка на дело: {hit['_source']['URL']}" for hit in
                 search_result["hits"]]
        return self.llm_client.analyze(query=request.query, documents=texts)
