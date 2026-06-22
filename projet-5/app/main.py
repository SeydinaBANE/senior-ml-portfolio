from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import agents, auth, billing, health, run
from app.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(title="Agent Platform", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["auth"])
app.include_router(agents.router, prefix=settings.api_v1_prefix, tags=["marketplace"])
app.include_router(run.router, prefix=settings.api_v1_prefix, tags=["run"])
app.include_router(billing.router, prefix=settings.api_v1_prefix, tags=["billing"])
