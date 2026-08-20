from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.core.security import get_password_hash
from app.features.v1.users import repository as user_repository
from app.features.v1.users import schema as user_schema


async def list_users(
    db: AsyncSession, role: str | None = None
) -> list[user_schema.UserRead]:
    users = await user_repository.list_users(db, role=role)
    return [user_schema.UserRead.model_validate(u) for u in users]


async def create_staff_user(
    db: AsyncSession, data: user_schema.UserCreate
) -> user_schema.UserRead:
    existing = await user_repository.get_by_email(db, data.email)
    if existing:
        raise ConflictException(detail="User with this email already exists")

    hashed_pw = get_password_hash(data.password)
    user = await user_repository.create_user(
        db=db, user_create=data, hashed_password=hashed_pw, role="staff"
    )
    return user_schema.UserRead.model_validate(user)


async def toggle_user_active(
    db: AsyncSession, user_id: str
) -> user_schema.UserRead:
    user = await user_repository.toggle_user_active(db, user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    return user_schema.UserRead.model_validate(user)
