"""Authentication endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database import get_db
from app.dependencies.rate_limit import limiter
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens, user = await service.register(data)
    return success_response({"tokens": tokens.model_dump(), "user": user.model_dump()})


@router.post("/login", response_model=dict)
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens, user = await service.login(data)
    return success_response({"tokens": tokens.model_dump(), "user": user.model_dump()})


@router.post("/refresh", response_model=dict)
async def refresh_token(data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.refresh(data.refresh_token)
    return success_response(tokens.model_dump())
