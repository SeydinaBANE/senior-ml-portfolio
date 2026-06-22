from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"


PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {
        "agent:create", "agent:read", "agent:update", "agent:delete",
        "agent:publish", "billing:read", "user:manage",
    },
    Role.DEVELOPER: {
        "agent:create", "agent:read", "agent:update", "agent:delete",
        "billing:read",
    },
    Role.USER: {
        "agent:read",
    },
}


def has_permission(role: Role, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, set())
