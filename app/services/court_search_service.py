from typing import Dict, Any, List

from elastic_transport import ObjectApiResponse

from api.models.request.legal_search_request import LegalSearchRequest
from repositories.court_decision_repository import CourtDecisionRepository
from utils.nlp import extract_keywords_natasha


class CourtSearchService:
    def __init__(self, repository: CourtDecisionRepository):
        self.repo = repository

    async def smart_search(self, search_model: LegalSearchRequest) -> Dict[str, Any]:
        processed_query = extract_keywords_natasha(search_model.query)
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"text_of_decision": {"query": processed_query, "boost": 5.0}}},
                        {"match": {"text_of_decision": {"query": processed_query, "fuzziness": "AUTO", "boost": 2.0}}},
                        {"match": {"case_number": {"query": processed_query, "boost": 4.0}}},
                        {"match": {"court": {"query": processed_query, "boost": 3.0}}},
                        {"match": {"court.autocomplete": {"query": processed_query, "boost": 2.0}}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "highlight": {
                "fields": {
                    "text_of_decision": {"fragment_size": 750, "number_of_fragments": 3},
                    "court": {}, "case_number": {}
                }
            },
            "sort": [{"_score": "desc"}, {"date": "desc"}],
            "size": search_model.limit,
            "from": search_model.from_,
            "aggs": {
                "courts": {"terms": {"field": "court.keyword", "size": 10}},
                "regions": {"terms": {"field": "court_region", "size": 10}},
                "categories": {"terms": {"field": "case_category", "size": 10}},
                "years": {"terms": {"field": "year", "size": 10}}
            }
        }

        if search_model.filters:
            query_body["query"]["bool"]["filter"] = []
            if search_model.filters.get("court_region"):
                query_body["query"]["bool"]["filter"].append(
                    {"term": {"court_region": search_model.filters["court_region"]}})
            if search_model.filters.get("case_category"):
                query_body["query"]["bool"]["filter"].append(
                    {"term": {"case_category": search_model.filters["case_category"]}})
            if search_model.filters.get("date_from") or search_model.filters.get("date_to"):
                range_filter = {}
                if search_model.filters.get("date_from"):
                    range_filter["gte"] = search_model.filters["date_from"]
                if search_model.filters.get("date_to"):
                    range_filter["lte"] = search_model.filters["date_to"]
                query_body["query"]["bool"]["filter"].append({"range": {"date": range_filter}})
        result = self.repo.search(query_body)
        hits = result.body["hits"]
        return hits



    def get_similar_cases(self, case_id: str, size: int = 5) -> List[Dict]:
        doc = self.repo.get_by_id(case_id)
        like_text = doc["_source"]["text_of_decision"]
        query_body = {
            "query": {
                "more_like_this": {
                    "fields": ["text_of_decision"],
                    "like": like_text,
                    "min_term_freq": 2,
                    "max_query_terms": 25,
                    "minimum_should_match": "20%"
                }
            },
            "size": size
        }
        result = self.repo.search(query_body)
        return [{
            "id": hit["_id"],
            "score": hit["_score"],
            "case_number": hit["_source"]["case_number"],
            "court": hit["_source"]["court"],
            "date": hit["_source"]["date"]
        } for hit in result["hits"]["hits"]]

    def get_index_stats(self) -> Dict[str, Any]:
        return self.repo.get_stats()
