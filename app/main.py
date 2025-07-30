import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.dependencies import Elasticsearch
from api.routes.search import router as search_router
from api.routes.stats import router as stats_router

app = FastAPI()

app.include_router(search_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    Elasticsearch.close()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True, host="0.0.0.0")
