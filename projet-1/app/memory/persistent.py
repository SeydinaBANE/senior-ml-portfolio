from uuid import UUID

from sqlalchemy import select

from app.db.models import ConversationMessage
from app.db.session import async_session


async def load_session_history(tenant_id: UUID, session_id: str) -> str:
    async with async_session() as db:
        result = await db.execute(
            select(ConversationMessage)
            .where(
                ConversationMessage.tenant_id == tenant_id,
                ConversationMessage.session_id == session_id,
            )
            .order_by(ConversationMessage.created_at)
            .limit(20)
        )
        messages = result.scalars().all()
        return "\n".join(f"{m.role}: {m.content}" for m in messages)


async def save_message(
    tenant_id: UUID, session_id: str, role: str, content: str
) -> None:
    async with async_session() as db:
        db.add(
            ConversationMessage(
                tenant_id=tenant_id,
                session_id=session_id,
                role=role,
                content=content,
            )
        )
        await db.commit()
