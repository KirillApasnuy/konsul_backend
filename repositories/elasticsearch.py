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
