from dataclasses import dataclass
from enum import StrEnum


class GuardrailVerdict(StrEnum):
    SAFE = "safe"
    UNSAFE = "unsafe"


@dataclass
class GuardrailResult:
    verdict: GuardrailVerdict
    category: str | None = None
