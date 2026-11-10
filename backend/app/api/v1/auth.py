"""
Auth Endpoints
==============
POST /auth/register   — Create account
POST /auth/login      — Login, receive HttpOnly JWT cookie
POST /auth/logout     — Clear session cookie
GET  /auth/me         — Get current authenticated user
"""

from fastapi import APIRouter, Depends, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.dependencies import get_db, get_current_user_id
from app.repositories.user_repository import UserRepository
from app.modules.auth.service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, AuthUserResponse

router = APIRouter()

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60  # 1 hour in seconds


def _set_auth_cookie(response: Response, token: str) -> None:
    """Set the HttpOnly JWT cookie on the response."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,       # HTTPS only in production; allows HTTP in local development
        samesite="lax" if not settings.is_production else "strict",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Create a new user account and return a JWT session cookie.
    Returns 409 if the email is already registered.
    """
    service = AuthService(UserRepository(db))
    user, token = await service.register(request)
    _set_auth_cookie(response, token)
    return user


@router.post(
    "/login",
    response_model=AuthUserResponse,
    summary="Login and receive session cookie",
)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Authenticate with email and password.
    Returns a JWT cookie on success, 401 on invalid credentials.
    """
    service = AuthService(UserRepository(db))
    user, token = await service.login(request)
    _set_auth_cookie(response, token)
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and clear session cookie",
)
async def logout(response: Response):
    """Clear the JWT session cookie."""
    response.delete_cookie(key=COOKIE_NAME, path="/")


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="Get current authenticated user",
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return the currently authenticated user. Requires valid session cookie."""
    repo = UserRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    profile = await repo.get_profile(user_id)
    language = profile.get("language", "en") if profile else "en"
    return AuthUserResponse(
        id=str(user["_id"]),
        email=user["email"],
        language=language,
    )
