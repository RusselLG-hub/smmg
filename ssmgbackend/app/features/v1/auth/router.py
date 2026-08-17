from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import get_db
from app.features.v1.auth import schema as auth_schema
from app.features.v1.auth import service as auth_service
from app.features.v1.auth.dependencies import get_current_user
from app.features.v1.users import model as user_model
from app.features.v1.users import schema as user_schema

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/register", response_model=auth_schema.AuthResponse, status_code=202)
@limiter.limit("5/minute")
async def register(
    request: Request,
    register_data: auth_schema.RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register(db, register_data)
    user_read = user_schema.UserRead.model_validate(user)
    return auth_schema.AuthResponse(
        user=user_read,
        message="Registration pending. Please check your email for the verification code.",
    )


@router.post("/verify-email", response_model=auth_schema.AuthResponse)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    verify_data: auth_schema.VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.verify_email(db, verify_data)
    user_read = user_schema.UserRead.model_validate(user)
    return auth_schema.AuthResponse(
        user=user_read,
        message="Email verified successfully. You may now log in.",
    )


@router.post("/verify-email/resend", response_model=auth_schema.MessageResponse)
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    resend_data: auth_schema.ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    await auth_service.resend_verification(db, resend_data.email)
    return auth_schema.MessageResponse(
        message="If the email exists and is unverified, a new code has been sent."
    )


@router.post("/login", response_model=auth_schema.AuthResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    login_data: auth_schema.LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user, token = await auth_service.login(db, login_data)

    # Remove the legacy API-host-only cookie before issuing the shared
    # frontend/API domain cookie.
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME)
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        domain=settings.AUTH_COOKIE_DOMAIN,
    )

    user_read = user_schema.UserRead.model_validate(user)
    return auth_schema.AuthResponse(
        user=user_read,
        message="Login successful.",
    )


@router.post("/logout", response_model=auth_schema.MessageResponse)
async def logout(response: Response):
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME)
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        domain=settings.AUTH_COOKIE_DOMAIN,
    )
    return auth_schema.MessageResponse(message="Logged out successfully.")


@router.get("/me", response_model=user_schema.UserRead)
async def get_me(
    current_user: user_model.User = Depends(get_current_user),
):
    return user_schema.UserRead.model_validate(current_user)


@router.patch("/me", response_model=user_schema.UserRead)
async def update_me(
    data: auth_schema.ProfileUpdateRequest,
    current_user: user_model.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.update_profile(db, current_user, data)
    return user_schema.UserRead.model_validate(user)


@router.post("/password-change/request", response_model=auth_schema.MessageResponse)
@limiter.limit("3/minute")
async def request_password_change(
    request: Request,
    current_user: user_model.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.request_password_change(db, current_user)
    return auth_schema.MessageResponse(
        message="A 6-digit verification code was sent to your email."
    )


@router.post("/password-change/confirm", response_model=auth_schema.MessageResponse)
@limiter.limit("5/minute")
async def confirm_password_change(
    request: Request,
    data: auth_schema.PasswordChangeConfirmRequest,
    current_user: user_model.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.confirm_password_change(db, current_user, data)
    return auth_schema.MessageResponse(message="Password changed successfully.")
