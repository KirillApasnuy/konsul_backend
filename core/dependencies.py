from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.repositories.elasticsearch import ElasticsearchRepository
from app.repositories.mongo import MongoRepository
from app.services.search_service import SearchService
from app.settings import Settings

settings = Settings()

mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_collection = mongo_client[settings.MONGO_DB][settings.MONGO_COLLECTION]
es_client = AsyncElasticsearch(settings.ES_HOST)


def get_mongo_repo() -> MongoRepository:
    return MongoRepository(mongo_collection)


def get_es_repo() -> ElasticsearchRepository:
    return ElasticsearchRepository(es_client, settings.ES_INDEX)


def get_search_service(
        es_repo: ElasticsearchRepository = Depends(get_es_repo),
        mongo_repo: MongoRepository = Depends(get_mongo_repo)
) -> SearchService:
    return SearchService(es_repo, mongo_repo)
