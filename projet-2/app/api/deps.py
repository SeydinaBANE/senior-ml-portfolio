from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict[str, str]:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return {"user_id": payload["sub"], "tenant_id": payload["tenant_id"]}
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


def get_tenant_id(user: dict[str, str] = Depends(get_current_user)) -> UUID:
    return UUID(user["tenant_id"])


def get_user_id(user: dict[str, str] = Depends(get_current_user)) -> str:
    return user["user_id"]
