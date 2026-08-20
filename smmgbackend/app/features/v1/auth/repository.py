from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.auth.model import VerificationCode


async def create_verification_code(
    db: AsyncSession,
    user_id: str,
    code_hash: str,
    expires_minutes: int = 15,
    purpose: str = "email_verification",
) -> VerificationCode:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    record = VerificationCode(
        user_id=user_id,
        purpose=purpose,
        code_hash=code_hash,
        expires_at=expires_at,
        is_consumed=False,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_latest_active_code(
    db: AsyncSession,
    user_id: str,
    purpose: str = "email_verification",
) -> VerificationCode | None:
    now = datetime.now(timezone.utc)
    stmt = (
        select(VerificationCode)
        .where(
            VerificationCode.user_id == user_id,
            VerificationCode.purpose == purpose,
            VerificationCode.is_consumed == False,
            VerificationCode.expires_at > now,
        )
        .order_by(VerificationCode.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def mark_code_consumed(db: AsyncSession, code_id: str) -> None:
    result = await db.execute(
        select(VerificationCode).where(VerificationCode.id == code_id)
    )
    code_record = result.scalar_one_or_none()
    if code_record:
        code_record.is_consumed = True
        await db.commit()
