from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


class TokenPayload(BaseModel):
    sub: str
    tenant_id: str
    exp: datetime


def create_access_token(user_id: str, tenant_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "tenant_id": str(tenant_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    try:
        raw = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**raw)
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
