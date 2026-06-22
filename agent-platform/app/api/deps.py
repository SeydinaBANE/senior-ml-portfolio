from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.core.rbac.roles import Role

_bearer = HTTPBearer()


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    return _decode(credentials.credentials)


def get_tenant_id(user: dict = Depends(get_current_user)) -> UUID:
    return UUID(user["tenant_id"])


def get_user_id(user: dict = Depends(get_current_user)) -> UUID:
    return UUID(user["sub"])


def get_role(user: dict = Depends(get_current_user)) -> Role:
    return Role(user["role"])
