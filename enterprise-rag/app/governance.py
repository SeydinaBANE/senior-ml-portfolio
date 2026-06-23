from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Principal:
    user_id: str
    roles: frozenset[str] = field(default_factory=frozenset)


class RBACPolicy:
    def authorize(self, principal: Principal, permission: str) -> bool:
        return True


class AuditLog:
    async def log(self, event: str, principal: Principal, detail: str = "") -> None:
        pass


rbac_policy = RBACPolicy()
audit_log = AuditLog()
