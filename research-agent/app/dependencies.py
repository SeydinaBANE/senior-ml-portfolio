from __future__ import annotations

from fastapi import Header, HTTPException

from app.config import settings
from app.governance import Principal, audit_log, rbac_policy


def get_principal(
    x_api_key: str = Header(..., description="API key for authentication"),
) -> Principal:
    role = settings.api_key_mapping.get(x_api_key)
    if role is None:
        raise HTTPException(status_code=401, detail="invalid API key")
    return Principal(user_id=f"key:{x_api_key[:8]}", roles=frozenset({role}))


def get_rbac_policy() -> RBACPolicy:
    return rbac_policy


def get_audit_log() -> AuditLog:
    return audit_log
