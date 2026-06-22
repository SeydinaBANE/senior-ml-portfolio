from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.routes import chat, health
from app.config import settings
from app.db.session import engine
from app.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_tracing()
    yield
    await engine.dispose()


app = FastAPI(
    title="Enterprise AI Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix=settings.api_v1_prefix, tags=["chat"])
