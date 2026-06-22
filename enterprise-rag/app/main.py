from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.routes import health, ingest, query
from app.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(title="Enterprise RAG", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, tags=["health"])
app.include_router(query.router, prefix=settings.api_v1_prefix, tags=["query"])
app.include_router(ingest.router, prefix=settings.api_v1_prefix, tags=["ingest"])
