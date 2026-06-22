import datetime as dt

from fastapi import APIRouter, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select

from app.config import settings
from app.db.models import User
from app.db.session import async_session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_token(user: User) -> str:
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role,
            "exp": expire,
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> UserResponse:
    async with async_session() as db:
        existing = await db.execute(select(User).where(User.email == body.email))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        user = User(
            email=body.email,
            hashed_password=_pwd.hash(body.password),
            tenant_id=body.tenant_id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return UserResponse(id=user.id, email=user.email, role=user.role, tenant_id=user.tenant_id)


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()

    if not user or not _pwd.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return TokenResponse(access_token=_create_token(user))
