import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.memory.persistent import load_session_history, save_message


@pytest.mark.asyncio
async def test_save_message_adds_and_commits() -> None:
    tenant_id = uuid.uuid4()

    with patch("app.memory.persistent.async_session") as mock_ctx:
        mock_db = AsyncMock()
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        await save_message(tenant_id, "sess-1", "user", "Bonjour")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_session_history_formats_chronologically() -> None:
    tenant_id = uuid.uuid4()
    msg1 = MagicMock(role="user", content="Bonjour")
    msg2 = MagicMock(role="assistant", content="Bonjour à vous!")

    with patch("app.memory.persistent.async_session") as mock_ctx:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [msg1, msg2]
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        history = await load_session_history(tenant_id, "sess-1")

    assert "user: Bonjour" in history
    assert "assistant: Bonjour à vous!" in history


@pytest.mark.asyncio
async def test_load_session_history_empty_when_no_messages() -> None:
    tenant_id = uuid.uuid4()

    with patch("app.memory.persistent.async_session") as mock_ctx:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        history = await load_session_history(tenant_id, "sess-empty")

    assert history == ""
