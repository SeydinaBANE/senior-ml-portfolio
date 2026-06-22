from langchain_core.tools import tool
from sqlalchemy import text

from app.db.session import async_session


@tool
async def query_database_tool(sql: str) -> str:
    """Execute a read-only SQL query and return results as a string."""
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")
    async with async_session() as db:
        result = await db.execute(text(sql))
        rows = result.fetchall()
        return str(rows[:50])
