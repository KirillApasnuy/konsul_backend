# services/search_service.py
from bson import ObjectId
from openai import AsyncOpenAI

from app import settings
from app.repositories.elasticsearch import ElasticsearchRepository
from app.repositories.mongo import MongoRepository
from app.settings import Settings
from app.utils.utils import parse_query

settings = Settings()

openai_client = AsyncOpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_URL)


class SearchService:
    def __init__(self, es_repo: ElasticsearchRepository, mongo_repo: MongoRepository):
        self.es_repo = es_repo
        self.mongo_repo = mongo_repo

    async def search_documents(self, query: str, limit: int):
        phrases, rest_query = parse_query(query)

        must_clauses = [{"match_phrase": {"full_text": phrase}} for phrase in phrases]
        if rest_query:
            must_clauses.append({"match": {"full_text": rest_query}})

        es_response = await self.es_repo.search(must_clauses, limit)
        hits = es_response["hits"]["hits"]
        ids = [ObjectId(hit["_id"]) for hit in hits]

        results = await self.mongo_repo.find_by_ids(ids, limit)

        id_to_doc = {doc["_id"]: doc for doc in results}
        ordered_results = []
        for hit in hits:
            doc_id = ObjectId(hit["_id"])
            doc = id_to_doc.get(doc_id)
            if doc:
                highlight = hit.get("highlight", {}).get("full_text", [])
                doc["highlight"] = highlight
                ordered_results.append(doc)

        for doc in ordered_results:
            doc["_id"] = str(doc["_id"])
            doc.pop("full_text", None)

        return ordered_results

    async def get_all_court_names(self):
        court_names = await self.mongo_repo.get_all_court_name()
        return court_names

    async def get_all_categories(self):
        categories = await self.mongo_repo.get_all_categories()
        for category in categories:
            if category == "" or category is None or len(category) == 0:
                categories.remove(category)
        return categories

    async def get_subcategories_by_category(self, category):
        return await self.mongo_repo.get_subcategories_by_category(category)

    async def search_with_summary(self, query: str, limit: int = 10):
        results = await self.search_documents(query, limit)

        # Подготовим текст для LLM
        docs_text = "\n\n".join(
            f"Документ #{i + 1}: {doc}"
            f"Ссылка на решение: {doc.get('url')}"
            for i, doc in enumerate(results)
        )

        system_prompt = (
            "Ты юридический помощник. На основе приведенных фрагментов судебных решений, "
            "сделай вывод, полезный юристу. "
            "Если решений мало, укажи это."
            """Требуемый вывод	Детализация
                Краткая справка	Наименование компании, регион регистрации, отрасль деятельности (если имеется)
                Судебная статистика	
                • Общее число дел за последние 3 года.
                • Сколько дел выиграно / проиграно.
                • Общая сумма исковых требований и фактически взысканная сумма.
                • Средняя продолжительность процессов.
                Топ-5 наиболее значимых дел по суммам	Номер, дата, суд, предмет спора, результат, ссылка на решение.
                """
            "Используй только приведённую информацию, не используй никаких дополнительных источников."
            "Если имеются, добавляй ссылки на документы"
        )

        completion = await openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": docs_text}
            ],
            temperature=0.3,
        )

        summary = completion.choices[0].message.content.strip()
        return {
            "documents": results,
            "summary": summary
        }
