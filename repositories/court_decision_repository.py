from typing import List, Dict, Any

from elasticsearch import Elasticsearch, helpers


class CourtDecisionRepository:
    def __init__(self, es: Elasticsearch, index_name: str):
        self.es = es
        self.index_name = index_name

    def create_index(self, settings: Dict[str, Any]) -> bool:
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, body=settings)
        return True

    def bulk_index(self, records: List[Dict[str, Any]]) -> int:
        actions = [{"_index": self.index_name, "_source": r} for r in records]
        helpers.bulk(self.es, actions)
        return len(actions)

    def search(self, body: Dict[str, Any]) -> Dict:
        return self.es.search(index=self.index_name, body=body)

    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        return self.es.get(index=self.index_name, id=doc_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "count": self.es.count(index=self.index_name)["count"],
            "size": self.es.indices.stats(index=self.index_name)["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
            "segments": self.es.indices.stats(index=self.index_name)["indices"][self.index_name]["total"]["segments"]["count"]
        }
