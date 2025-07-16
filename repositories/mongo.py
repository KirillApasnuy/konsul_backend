from typing import List

from motor.motor_asyncio import AsyncIOMotorCollection


class MongoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_by_ids(self, ids, limit):
        cursor = self.collection.find({"_id": {"$in": ids}})
        return await cursor.to_list(length=limit)

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