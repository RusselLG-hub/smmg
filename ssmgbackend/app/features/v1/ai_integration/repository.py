from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.ai_integration.model import AIChatMessage, AIChatSession


async def create_session(
    db: AsyncSession, user_id: str, title: str | None = None
) -> AIChatSession:
    session = AIChatSession(
        user_id=user_id,
        title=title.strip() if title else "New Consultation Chat",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session_by_id(
    db: AsyncSession, session_id: str
) -> AIChatSession | None:
    stmt = select(AIChatSession).where(AIChatSession.id == session_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_user_sessions(
    db: AsyncSession, user_id: str
) -> list[AIChatSession]:
    stmt = (
        select(AIChatSession)
        .where(AIChatSession.user_id == user_id)
        .order_by(AIChatSession.updated_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_session(db: AsyncSession, session: AIChatSession) -> None:
    await db.delete(session)
    await db.commit()


async def create_message(
    db: AsyncSession, session_id: str, role: str, content: str
) -> AIChatMessage:
    msg = AIChatMessage(
        session_id=session_id,
        role=role,
        content=content.strip(),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_recent_messages(
    db: AsyncSession, session_id: str, limit: int = 10
) -> list[AIChatMessage]:
    stmt = (
        select(AIChatMessage)
        .where(AIChatMessage.session_id == session_id)
        .order_by(AIChatMessage.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    msgs = list(result.scalars().all())
    msgs.reverse()  # Return in chronological order
    return msgs


async def touch_session_title(
    db: AsyncSession, session: AIChatSession, first_msg_content: str
) -> None:
    if not session.title or session.title == "New Consultation Chat":
        # Truncate first message to create title
        clean_title = first_msg_content.strip()
        if len(clean_title) > 40:
            clean_title = clean_title[:37] + "..."
        session.title = clean_title
    session.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
