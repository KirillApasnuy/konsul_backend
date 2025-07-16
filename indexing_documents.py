import asyncio

from elasticsearch import AsyncElasticsearch, helpers
from motor.motor_asyncio import AsyncIOMotorClient
from tqdm.asyncio import tqdm_asyncio

MONGO_URI = "mongodb://localhost:27017"
ES_HOST = "http://localhost:9200"
MONGO_DB = "konsul-db"
MONGO_COLLECTION = "konsul"
ES_INDEX = "documents"

CHUNK_SIZE = 1000


async def get_documents():
    client = AsyncIOMotorClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]
    cursor = collection.find({}, {"_id": 1, "full_text": 1})
    async for doc in cursor:
        yield {
            "_index": ES_INDEX,
            "_id": str(doc["_id"]),
            "_source": {
                "full_text": doc["full_text"]
            }
        }


async def count_documents():
    client = AsyncIOMotorClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]
    return await collection.count_documents({})


async def chunked(aiter, size):
    chunk = []
    async for item in aiter:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


async def index_to_es():
    total_docs = await count_documents()
    es = AsyncElasticsearch(ES_HOST)

    # Удаление и создание индекса
    await es.options(ignore_status=[400, 404]).indices.delete(index=ES_INDEX)
    await es.indices.create(index=ES_INDEX, body={
        "mappings": {
            "properties": {
                "full_text": {"type": "text"}
            }
        }
    })

    progress = tqdm_asyncio(total=total_docs, desc="Indexing documents", unit="docs")

    async for chunk in chunked(get_documents(), CHUNK_SIZE):
        await helpers.async_bulk(es, chunk)
        progress.update(len(chunk))

    await es.close()
    progress.close()


if __name__ == "__main__":
    asyncio.run(index_to_es())
