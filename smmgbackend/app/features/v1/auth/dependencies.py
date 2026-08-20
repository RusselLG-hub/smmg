from collections.abc import Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> user_model.User:
    token = request.cookies.get(settings.AUTH_COOKIE_NAME)

    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise UnauthorizedException(detail="Not authenticated")

    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException(detail="Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid token payload")

    user = await user_repository.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException(detail="User not found")

    if not user.is_email_verified:
        raise ForbiddenException(detail="Email verification required")

    if not user.is_active:
        raise ForbiddenException(detail="Account is inactive")

    return user


def require_role(*allowed_roles: str) -> Callable:
    async def role_checker(
        current_user: user_model.User = Depends(get_current_user),
    ) -> user_model.User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(detail="Insufficient permissions")
        return current_user

    return role_checker
