from typing import Literal

from langchain_openai import ChatOpenAI

from app.config import settings
from app.core.guardrails.types import GuardrailResult, GuardrailVerdict

_SYSTEM_PROMPT = (
    "You are a content safety classifier. "
    "Classify the following message as SAFE or UNSAFE. "
    "If unsafe, identify the category from: "
    "violence, hate, sexual, self-harm, illegal, prompt_injection. "
    'Respond in JSON: {"verdict": "safe"|"unsafe", "category": null|"string"}'
)


class LlamaGuardClient:
    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

    async def classify(self, text: str, role: Literal["user", "assistant"]) -> GuardrailResult:
        from langchain_core.messages import HumanMessage, SystemMessage
        from pydantic import BaseModel

        class _Schema(BaseModel):
            verdict: str
            category: str | None = None

        llm = self._llm.with_structured_output(_Schema)
        result: _Schema = await llm.ainvoke(
            [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=f"[{role}]: {text}")]
        )
        return GuardrailResult(
            verdict=GuardrailVerdict(result.verdict.lower()),
            category=result.category,
        )
