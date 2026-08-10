from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    generate_verification_code,
    hash_password,
    verify_password,
)
from app.features.v1.auth import repository as auth_repository
from app.features.v1.auth import schema as auth_schema
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository
from app.providers import resend_provider


async def register(
    db: AsyncSession, register_data: auth_schema.RegisterRequest
) -> user_model.User:
    existing_user = await user_repository.get_by_email(db, register_data.email)
    if existing_user:
        raise ConflictException(detail="Email is already registered")

    hashed_pw = hash_password(register_data.password)
    user_create = user_schema.UserCreate(
        email=register_data.email,
        name=register_data.name,
        password=register_data.password,
    )
    user = await user_repository.create_user(
        db, user_create=user_create, hashed_password=hashed_pw, role="patient"
    )

    await send_verification_code(db, user=user)
    return user


async def send_verification_code(
    db: AsyncSession, user: user_model.User
) -> None:
    if user.is_email_verified:
        raise BadRequestException(detail="Email is already verified")

    code = generate_verification_code()
    code_hash = hash_password(code)

    await auth_repository.create_verification_code(
        db, user_id=user.id, code_hash=code_hash, expires_minutes=15
    )

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e5e7eb; rounded-lg: 8px;">
        <h2 style="color: #2563eb; margin-bottom: 16px;">Welcome to SSMG Healthcare</h2>
        <p>Hello {user.name},</p>
        <p>Thank you for registering. Your verification code is:</p>
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; font-size: 28px; font-weight: bold; text-align: center; padding: 16px; border-radius: 8px; letter-spacing: 4px; margin: 20px 0;">
            {code}
        </div>
        <p style="color: #4b5563; font-size: 14px;">This code will expire in 15 minutes. If you did not request this, please ignore this email.</p>
    </div>
    """

    resend_provider.send_email(
        to=user.email,
        subject="SSMG — Verify Your Email",
        html=html_content,
    )


async def resend_verification(
    db: AsyncSession, email: str
) -> None:
    user = await user_repository.get_by_email(db, email)
    if not user:
        # Don't expose whether user exists
        return

    if user.is_email_verified:
        raise BadRequestException(detail="Email is already verified")

    await send_verification_code(db, user=user)


async def verify_email(
    db: AsyncSession, verify_data: auth_schema.VerifyEmailRequest
) -> user_model.User:
    user = await user_repository.get_by_email(db, verify_data.email)
    if not user:
        raise BadRequestException(detail="Invalid verification request")

    if user.is_email_verified:
        raise BadRequestException(detail="Email is already verified")

    active_code = await auth_repository.get_latest_active_code(
        db, user_id=user.id, purpose="email_verification"
    )
    if not active_code:
        raise BadRequestException(detail="Verification code has expired or is invalid")

    if not verify_password(verify_data.code, active_code.code_hash):
        raise BadRequestException(detail="Invalid verification code")

    await auth_repository.mark_code_consumed(db, active_code.id)
    updated_user = await user_repository.mark_email_verified(db, user.id)
    return updated_user or user


async def login(
    db: AsyncSession, login_data: auth_schema.LoginRequest
) -> tuple[user_model.User, str]:
    user = await user_repository.get_by_email(db, login_data.email)
    if not user:
        raise UnauthorizedException(detail="Invalid email or password")

    if not verify_password(login_data.password, user.hashed_password):
        raise UnauthorizedException(detail="Invalid email or password")

    if not user.is_active:
        raise ForbiddenException(detail="Account is inactive")

    if not user.is_email_verified:
        raise ForbiddenException(detail="Email not verified. Please verify your email before logging in.")

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return user, token
