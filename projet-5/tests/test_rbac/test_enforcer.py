import pytest
from fastapi import HTTPException

from app.core.rbac.enforcer import require_permission
from app.core.rbac.roles import Role


def test_admin_has_all_permissions() -> None:
    require_permission("agent:create")(Role.ADMIN)
    require_permission("agent:delete")(Role.ADMIN)
    require_permission("agent:publish")(Role.ADMIN)
    require_permission("billing:read")(Role.ADMIN)
    require_permission("user:manage")(Role.ADMIN)


def test_user_cannot_create_agent() -> None:
    with pytest.raises(HTTPException) as exc:
        require_permission("agent:create")(Role.USER)
    assert exc.value.status_code == 403


def test_developer_cannot_manage_users() -> None:
    with pytest.raises(HTTPException) as exc:
        require_permission("user:manage")(Role.DEVELOPER)
    assert exc.value.status_code == 403


def test_developer_can_create_and_delete() -> None:
    require_permission("agent:create")(Role.DEVELOPER)
    require_permission("agent:delete")(Role.DEVELOPER)
