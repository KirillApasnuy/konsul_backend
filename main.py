import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.controllers.search import router as search_router
from core.dependencies import es_client, mongo_client

app = FastAPI()

app.include_router(search_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (для разработки). Лучше указать конкретные в проде.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown():
    await es_client.close()
    mongo_client.close()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True, host="0.0.0.0")
