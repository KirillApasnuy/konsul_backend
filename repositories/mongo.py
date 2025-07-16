from typing import List, Optional, Dict

from motor.motor_asyncio import AsyncIOMotorCollection


class MongoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_by_ids(self, ids, limit):
        cursor = self.collection.find({"_id": {"$in": ids}})
        return await cursor.to_list(length=limit)

    async def find_by_case_number(self, case_number: str) -> Optional[Dict]:
        """
        Поиск документа по номеру дела
        """
        return await self.collection.find_one({"case_number": case_number})

    async def find_by_case_numbers(self, case_numbers: List[str]) -> List[Dict]:
        """
        Поиск документов по списку номеров дел
        """
        cursor = self.collection.find({"case_number": {"$in": case_numbers}})
        return await cursor.to_list(length=None)

    async def get_all_court_name(self) -> List[str]:
        court_names = await self.collection.distinct("court_info.court_name")
        return court_names

    async def get_all_categories(self) -> List[str]:
        categories = await self.collection.distinct("court_info.category")
        return categories

    async def get_subcategories_by_category(self, category: str) -> List[str]:
        subcategories = await self.collection.distinct(
            "court_info.subcategory",
            {"court_info.category": category}  # фильтр по категории
        )
        return subcategories

    async def get_cases_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Получение дел за определенный период
        """
        cursor = self.collection.find({
            "decision_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        return await cursor.to_list(length=None)

    async def get_case_statistics(self, case_numbers: List[str]) -> Dict:
        """
        Получение статистики по делам
        """
        pipeline = [
            {"$match": {"case_number": {"$in": case_numbers}}},
            {"$group": {
                "_id": None,
                "total_cases": {"$sum": 1},
                "courts": {"$addToSet": "$court_name"},
                "categories": {"$addToSet": "$category"},
                "avg_duration": {"$avg": "$duration_days"}
            }}
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0] if result else {}
