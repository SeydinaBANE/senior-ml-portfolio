from app.core.guardrails.injection import detect_injection
from app.core.guardrails.llamaguard import LlamaGuardClient
from app.core.guardrails.types import GuardrailResult, GuardrailVerdict
from app.observability.metrics import guardrail_violations_total

__all__ = ["GuardrailResult", "GuardrailVerdict", "check_input", "check_output"]

_llamaguard = LlamaGuardClient()


async def check_input(text: str, tenant_id: str) -> GuardrailResult:
    injection = await detect_injection(text)
    if injection.is_injection:
        guardrail_violations_total.labels(tenant_id=tenant_id, direction="input").inc()
        return GuardrailResult(verdict=GuardrailVerdict.UNSAFE, category="prompt_injection")

    result = await _llamaguard.classify(text, role="user")
    if result.verdict == GuardrailVerdict.UNSAFE:
        guardrail_violations_total.labels(tenant_id=tenant_id, direction="input").inc()
    return result


async def check_output(text: str, tenant_id: str) -> GuardrailResult:
    result = await _llamaguard.classify(text, role="assistant")
    if result.verdict == GuardrailVerdict.UNSAFE:
        guardrail_violations_total.labels(tenant_id=tenant_id, direction="output").inc()
    return result
