from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from repositories.elasticsearch import ElasticsearchRepository
from repositories.mongo import MongoRepository
from services.search_service import SearchService
from settings import Settings

settings = Settings()

mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_collection = mongo_client[settings.MONGO_DB][settings.MONGO_COLLECTION]
mongo_collection_ss = mongo_client[settings.MONGO_DB_SS][settings.MONGO_COLLECTION]
es_client = AsyncElasticsearch(settings.ES_HOST)



def get_mongo_repo() -> MongoRepository:
    return MongoRepository(mongo_collection)

def get_mongo_repo_ss() -> MongoRepository:
    return MongoRepository(mongo_collection_ss)

def get_es_repo() -> ElasticsearchRepository:
    return ElasticsearchRepository(es_client, settings.ES_INDEX)

def get_es_repo_ss() -> ElasticsearchRepository:
    return ElasticsearchRepository(es_client, settings.ES_INDEX_SS)

def get_search_service(
        es_repo: ElasticsearchRepository = Depends(get_es_repo),
        es_repo_ss: ElasticsearchRepository = Depends(get_es_repo_ss),
        mongo_repo: MongoRepository = Depends(get_mongo_repo),
        mongo_repo_ss: MongoRepository = Depends(get_mongo_repo_ss),
) -> SearchService:
    return SearchService(es_repo, es_repo_ss, mongo_repo, mongo_repo_ss)
