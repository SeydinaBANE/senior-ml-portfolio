import re

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"you are now",
    r"forget (your|all) (previous )?instructions",
    r"act as (a |an )?(?!assistant)",
    r"jailbreak",
    r"DAN mode",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

MAX_INPUT_LENGTH = 4000


class PromptInjectionError(ValueError):
    pass


def validate_input(text: str) -> str:
    if len(text) > MAX_INPUT_LENGTH:
        raise PromptInjectionError("Input exceeds maximum allowed length.")
    for pattern in _compiled:
        if pattern.search(text):
            raise PromptInjectionError("Potential prompt injection detected.")
    return text
