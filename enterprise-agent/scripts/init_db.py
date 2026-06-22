"""Create all database tables and enable the pgvector extension."""
import asyncio

import sqlalchemy as sa

from app.db.models import Base
from app.db.session import engine


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Database initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
