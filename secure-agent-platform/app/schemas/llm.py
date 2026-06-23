"""Schemas partages : messages et requetes/reponses LLM."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Role d'un message dans une conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message echange avec le LLM."""

    role: Role
    content: str


class LLMRequest(BaseModel):
    """Requete adressee au gateway LLM."""

    messages: list[Message]
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class LLMResponse(BaseModel):
    """Reponse renvoyee par le gateway LLM."""

    content: str
    model: str
    used_fallback: bool = False
