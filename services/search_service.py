# services/search_service.py
from bson import ObjectId
from openai import AsyncOpenAI

from repositories.edmy import EdmyRepository
from repositories.elasticsearch import ElasticsearchRepository
from repositories.mongo import MongoRepository
from settings import Settings
from utils.utils import parse_query

settings = Settings()

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class SearchService:
    def __init__(self, es_repo: ElasticsearchRepository, es_repo_ss: ElasticsearchRepository, mongo_repo: MongoRepository, mongo_repo_ss: MongoRepository, ):
        self.es_repo = es_repo
        self.es_repo_ss = es_repo_ss
        self.mongo_repo = mongo_repo
        self.mongo_repo_ss = mongo_repo_ss
        self.edmy_repo = EdmyRepository(settings)

    async def search_documents(self, query: str, limit: int):
        phrases, rest_query = parse_query(query)

        must_clauses = []

        if phrases:
            must_clauses.extend([{"match_phrase": {"full_text": phrase}} for phrase in phrases])

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

    async def search_legal_cases(self, query_text: str, limit: int = 15):
        """
        Поиск судебных дел с подсветкой фрагментов и полной информацией из MongoDB
        """
        try:
            # Поиск в Elasticsearch
            es_response = await self.es_repo.search_with_highlight(
                query={
                    "match": {
                        "text_of_decision": query_text
                    }
                },
                source_fields=["case_number", "URL"],
                highlight_fields={"text_of_decision": {}},
                size=limit
            )

            hits = es_response["hits"]["hits"]
            total_found = es_response["hits"]["total"]["value"]

            results = []

            for hit in hits:
                case_number = hit["_source"]["case_number"]
                url = hit["_source"].get("URL", "")
                highlight = hit.get("highlight", {}).get("text_of_decision", ["<нет фрагмента>"])[0]

                # Поиск полного документа в MongoDB
                full_doc = await self.mongo_repo_ss.find_by_case_number(case_number)

                if full_doc and "_id" in full_doc:
                    full_doc["_id"] = str(full_doc["_id"])

                result = {
                    "case_number": case_number,
                    "url": url,
                    "highlight": highlight,
                    "full_document": full_doc if full_doc else None
                }

                results.append(result)

            return {
                "total_found": total_found,
                "results": results
            }

        except Exception as e:
            raise Exception(f"Ошибка при поиске судебных дел: {str(e)}")

    async def analyze_legal_practice(self, query_text: str, limit: int = 15):
        """
        Анализ судебной практики с автоматическим определением предмета доказывания
        """
        try:
            # Получаем результаты поиска
            search_results = await self.search_legal_cases(query_text, limit)

            if not search_results["results"]:
                return {
                    "search_results": search_results,
                    "analysis": "Не найдено судебных решений по данному запросу"
                }

            # Подготавливаем данные для анализа
            cases_for_analysis = []
            for result in search_results["results"]:
                case_info = {
                    "case_number": result["case_number"],
                    "url": result["url"],
                    "highlight": result["highlight"],
                    "full_text": result["full_document"]["text_of_decision"] if result["full_document"] else ""
                }
                cases_for_analysis.append(case_info)

            # Формируем промпт для анализа
            analysis_prompt = f"""
            Проанализируй следующие судебные решения по теме: "{query_text}"

            Судебные дела:
            {cases_for_analysis}

            Проведи анализ и определи:
            1. Предмет доказывания по данной категории споров
            2. Основные способы доказывания, которые суды считают допустимыми
            3. Типичные ошибки сторон в доказывании
            4. Рекомендации по сбору доказательств
            5. Статистика успешности дел (если можно определить)

            Ответ структурируй в виде юридического заключения.
            """

            # Получаем анализ от LLM
            analysis = await self.edmy_repo.ask(
                messages=[
                    {"role": "assistant", "content": "Ты опытный юрист, специализирующийся на анализе судебной практики."},
                    {"role": "user", "content": analysis_prompt}
                ]
            )

            return {
                # "search_results": search_results,
                "analysis": analysis
            }

        except Exception as e:
            raise Exception(f"Ошибка при анализе судебной практики: {str(e)}")

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
                Краткая справка	Наименование компании, регио
                н регистрации, отрасль деятельности (если имеется)
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

        completion = await self.edmy_repo.ask(
            messages=[
                {"role": "user", "content": docs_text}
            ],
        )

        return {
            "documents": results,
            "summary": completion
        }


    async def debug_mongo_structure(self, limit: int = 5):
        """
        Отладочный метод для изучения структуры данных в MongoDB
        """
        try:
            # Получаем несколько документов для анализа структуры
            sample_docs = await self.mongo_repo_ss.collection.find().limit(limit).to_list(length=limit)

            structure_info = {
                "total_documents": await self.mongo_repo_ss.collection.count_documents({}),
                "sample_count": len(sample_docs),
                "field_names": [],
                "sample_case_numbers": []
            }

            if sample_docs:
                # Получаем все уникальные поля
                all_fields = set()
                for doc in sample_docs:
                    all_fields.update(doc.keys())

                    # Ищем поля, которые могут содержать номер дела
                    for field, value in doc.items():
                        if isinstance(value, str) and any(char in value for char in ['А', 'A', '-', '/']):
                            if field not in structure_info["sample_case_numbers"]:
                                structure_info["sample_case_numbers"].append({
                                    "field": field,
                                    "value": value[:50]  # Первые 50 символов
                                })

                structure_info["field_names"] = sorted(list(all_fields))

            return structure_info

        except Exception as e:
            return {"error": f"Ошибка при анализе структуры MongoDB: {str(e)}"}
