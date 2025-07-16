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
        Специализированный поиск судебных дел
        """
        return await self.search_with_highlight(
            query={
                "match": {
                    "text_of_decision": query_text
                }
            },
            source_fields=source_fields or ["case_number", "URL"],
            highlight_fields={"text_of_decision": {}},
            size=size
        )

