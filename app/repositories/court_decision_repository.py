from typing import List, Dict, Any

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch, helpers, RequestError


class CourtDecisionRepository:
    def __init__(self, es: Elasticsearch, index_name: str):
        self.es = es
        self.index_name = index_name

    def create_index(self) -> bool:
        """
        Создание индекса с оптимизированными настройками для русского языка
        """

        # Настройки индекса с русскими анализаторами
        index_settings = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1,
                "max_result_window": 50000,
                "analysis": {
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        },
                        "russian_morphology": {
                            "type": "hunspell",
                            "locale": "ru_RU"
                        },
                        "edge_ngram_filter": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 20
                        }
                    },
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "russian_stop",
                                "russian_stemmer"
                            ]
                        },
                        "russian_autocomplete": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "russian_stop",
                                "edge_ngram_filter"
                            ]
                        },
                        "case_number_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "court": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "russian_autocomplete",
                                "search_analyzer": "russian_analyzer"
                            }
                        }
                    },
                    "case_number": {
                        "type": "text",
                        "analyzer": "case_number_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "date": {
                        "type": "date",
                        "format": "dd.MM.yyyy||yyyy-MM-dd"
                    },
                    "text_of_decision": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "raw": {"type": "keyword", "ignore_above": 256}
                        }
                    },
                    "URL": {
                        "type": "keyword",
                        "index": False
                    },
                    "text_length": {
                        "type": "integer"
                    },
                    "year": {
                        "type": "integer"
                    },
                    "month": {
                        "type": "integer"
                    },
                    "court_region": {
                        "type": "keyword"
                    },
                    "case_category": {
                        "type": "keyword"
                    },
                    "text_hash": {
                        "type": "keyword"
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            }
        }

        try:
            # Удаление существующего индекса если есть
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)

            # Создание нового индекса
            self.es.indices.create(index=self.index_name, body=index_settings)
            return True

        except RequestError as e:
            return False

    def bulk_index(self, records: List[Dict[str, Any]]) -> int:
        actions = [{"_index": self.index_name, "_source": r} for r in records]
        helpers.bulk(self.es, actions)
        return len(actions)

    def search(self, body: Dict[str, Any]) -> ObjectApiResponse:
        return self.es.search(index=self.index_name, body=body)

    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        return self.es.get(index=self.index_name, id=doc_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "count": self.es.count(index=self.index_name)["count"],
            "size": self.es.indices.stats(index=self.index_name)["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
            "segments": self.es.indices.stats(index=self.index_name)["indices"][self.index_name]["total"]["segments"]["count"]
        }
