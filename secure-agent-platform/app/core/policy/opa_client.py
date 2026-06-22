from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings


@dataclass
class PolicyResult:
    allowed: bool
    reason: str


class OPAClient:
    def __init__(self) -> None:
        self._base_url = settings.opa_url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5))
    async def evaluate(self, policy_path: str, input_data: dict[str, Any]) -> PolicyResult:
        url = f"{self._base_url}/v1/data/{policy_path.replace('.', '/')}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"input": input_data})
            response.raise_for_status()
            result = response.json().get("result", {})
            return PolicyResult(
                allowed=result.get("allow", False),
                reason=result.get("reason", "policy denied"),
            )


opa_client = OPAClient()
