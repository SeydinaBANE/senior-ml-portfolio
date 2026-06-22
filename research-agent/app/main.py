from fastapi import FastAPI

from app.api.routes import health, research, tools
from app.config import settings

app = FastAPI(title="Research Agent", version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(research.router, prefix=settings.api_v1_prefix, tags=["research"])
app.include_router(tools.router, prefix=settings.api_v1_prefix, tags=["tools"])
