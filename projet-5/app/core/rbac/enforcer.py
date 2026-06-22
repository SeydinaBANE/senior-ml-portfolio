from collections.abc import Callable

from fastapi import HTTPException, status

from app.core.rbac.roles import Role, has_permission


def require_permission(permission: str) -> Callable[[Role], None]:
    def _check(role: Role) -> None:
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required.",
            )
    return _check
