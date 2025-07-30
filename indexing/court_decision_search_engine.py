import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Any, Optional

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourtDecisionSearchEngine:
    def __init__(self, es_host: str = "http://elasticsearch:9200", index_name: str = "court_decisions"):
        self.es = Elasticsearch(es_host)
        self.index_name = index_name

        # Проверка подключения
        if not self.es.ping():
            raise ConnectionError("Не удалось подключиться к Elasticsearch")

        logger.info(f"Подключение к Elasticsearch: {es_host}")

    def create_index(self) -> bool:

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
                            "raw": {"type": "keyword", "ignore_above": 512}
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
                logger.info(f"Удален существующий индекс: {self.index_name}")

            # Создание нового индекса
            self.es.indices.create(index=self.index_name, body=index_settings)
            logger.info(f"Создан индекс: {self.index_name}")
            return True

        except RequestError as e:
            logger.error(f"Ошибка создания индекса: {e}")
            return False

    def _extract_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        enriched = record.copy()

        text = record.get("text_of_decision", "")
        enriched["text_length"] = len(text)

        enriched["text_hash"] = hashlib.md5(text.encode()).hexdigest()

        date_str = record.get("date", "")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                enriched["year"] = date_obj.year
                enriched["month"] = date_obj.month
            except ValueError:
                enriched["year"] = None
                enriched["month"] = None

        court = record.get("court", "")
        if "Москв" in court:
            enriched["court_region"] = "Москва"
        elif "Петербург" in court or "СПб" in court:
            enriched["court_region"] = "Санкт-Петербург"
        elif "област" in court:
            enriched["court_region"] = "Область"
        else:
            enriched["court_region"] = "Другой"

        case_number = record.get("case_number", "")
        if case_number:
            if case_number.startswith("А"):
                enriched["case_category"] = "Арбитражный"
            elif case_number.startswith("К"):
                enriched["case_category"] = "Кассация"
            elif case_number.startswith("Г"):
                enriched["case_category"] = "Гражданский"
            else:
                enriched["case_category"] = "Другой"

        enriched["created_at"] = datetime.now().isoformat()

        return enriched

    def bulk_index_jsonl(self, jsonl_file_path: str, chunk_size: int = 1000,
                         max_workers: int = 4) -> bool:

        def process_chunk(chunk: List[Dict]):
            actions = []
            for record in chunk:
                enriched_record = self._extract_metadata(record)
                action = {
                    "_index": self.index_name,
                    "_source": enriched_record
                }
                actions.append(action)

            try:
                helpers.bulk(self.es, actions, chunk_size=chunk_size)
                return len(actions)
            except Exception as e:
                logger.error(f"Ошибка индексации чанка: {e}")
                return 0

        try:
            total_indexed = 0
            chunk = []

            logger.info(f"Начало индексации файла: {jsonl_file_path}")

            with open(jsonl_file_path, 'r', encoding='utf-8') as f:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []

                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            try:
                                record = json.loads(line)
                                chunk.append(record)

                                # Отправка чанка на обработку
                                if len(chunk) >= chunk_size:
                                    future = executor.submit(process_chunk, chunk)
                                    futures.append(future)
                                    chunk = []

                                    # Логирование прогресса
                                    if line_num % 10000 == 0:
                                        logger.info(f"Обработано строк: {line_num}")

                            except json.JSONDecodeError as e:
                                logger.warning(f"Ошибка JSON в строке {line_num}: {e}")
                                continue

                    if chunk:
                        future = executor.submit(process_chunk, chunk)
                        futures.append(future)

                    for future in futures:
                        total_indexed += future.result()

            logger.info(f"Индексация завершена. Проиндексировано записей: {total_indexed}")

            # Обновление индекса
            self.es.indices.refresh(index=self.index_name)
            return True

        except Exception as e:
            logger.error(f"Ошибка при индексации: {e}")
            return False

