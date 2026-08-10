from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.users.model import User
from app.features.v1.users.schema import UserCreate


async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, role: str | None = None) -> list[User]:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_user(
    db: AsyncSession,
    user_create: UserCreate,
    hashed_password: str,
    role: str = "patient",
) -> User:
    user = User(
        email=user_create.email.lower(),
        name=user_create.name.strip(),
        hashed_password=hashed_password,
        role=role,
        is_active=True,
        is_email_verified=(role != "patient"),  # Staff/Admin/Doctor auto-verified
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def mark_email_verified(db: AsyncSession, user_id: str) -> User | None:
    user = await get_by_id(db, user_id)
    if user:
        user.is_email_verified = True
        await db.commit()
        await db.refresh(user)
    return user


async def toggle_user_active(db: AsyncSession, user_id: str) -> User | None:
    user = await get_by_id(db, user_id)
    if user:
        user.is_active = not user.is_active
        await db.commit()
        await db.refresh(user)
    return user
