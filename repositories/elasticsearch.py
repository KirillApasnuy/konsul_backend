import re
from typing import Optional, List, Dict


class ElasticsearchRepository:
    def __init__(self, es_client, index):
        self.es_client = es_client
        self.index = index

    async def search(self, must_clauses, limit):
        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "size": limit,
            "highlight": {
                "fields": {
                    "full_text": {
                        "pre_tags": ["<em>"],
                        "post_tags": ["</em>"]
                    }
                }
            }
        }
        return await self.es_client.search(index=self.index, body=query)

    async def search_with_highlight(
            self,
            query: Dict,
            source_fields: Optional[List[str]] = None,
            highlight_fields: Optional[Dict] = None,
            size: int = 10
    ) -> Dict:
        """
        Поиск с подсветкой найденных фрагментов
        """
        search_body = {
            "query": query,
            "size": size
        }

        if source_fields:
            search_body["_source"] = source_fields

        if highlight_fields:
            search_body["highlight"] = {
                "fields": highlight_fields
            }

        response = await self.es_client.search(
            index="konsul_cases",
            body=search_body
        )
        return response

    async def search_legal_cases(
            self,
            query_text: str,
            source_fields: Optional[List[str]] = None,
            size: int = 15
    ) -> Dict:
        """
        Специализированный поиск судебных дел с поддержкой точных фраз в кавычках
        """
        # Находим точные фразы в кавычках (поддержка как одинарных, так и двойных)
        exact_phrases = re.findall(r'"([^"]+)"|«([^»]+)»|“([^”]+)”', query_text)
        # Выравниваем результат — оставляем только непустые группы
        exact_phrases = [phrase for group in exact_phrases for phrase in group if phrase]

        # Убираем точные фразы из основного текста (для "обычного" match)
        text_without_phrases = query_text
        for phrase in exact_phrases:
            text_without_phrases = text_without_phrases.replace(f'"{phrase}"', '')
            text_without_phrases = text_without_phrases.replace(f'«{phrase}»', '')
            text_without_phrases = text_without_phrases.replace(f'“{phrase}”', '')

        should_clauses = []

        # Добавляем обычный match, если остался текст
        if text_without_phrases.strip():
            should_clauses.append({
                "match": {
                    "text_of_decision": text_without_phrases.strip()
                }
            })

        # Добавляем точные фразы как match_phrase
        for phrase in exact_phrases:
            should_clauses.append({
                "match_phrase": {
                    "text_of_decision": phrase
                }
            })

        # Если нет ни обычного текста, ни точных фраз — fallback на пустой match_all
        query = {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1 if should_clauses else 0
            }
        } if should_clauses else {"match_all": {}}

        return await self.search_with_highlight(
            query=query,
            source_fields=source_fields or ["case_number", "URL"],
            highlight_fields={"text_of_decision": {}},
            size=size
        )

