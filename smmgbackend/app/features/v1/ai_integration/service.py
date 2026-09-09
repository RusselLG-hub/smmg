import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
)
from app.features.v1.ai_integration import prompts
from app.features.v1.ai_integration import repository as ai_repository
from app.features.v1.ai_integration import schema as ai_schema
from app.features.v1.users import model as user_model
from app.providers.ai_chat import AiProviderError, generate_chat_response

logger = logging.getLogger(__name__)


async def create_chat_session(
    db: AsyncSession, current_user: user_model.User, title: str | None = None
) -> ai_schema.AIChatSessionRead:
    session = await ai_repository.create_session(db, user_id=current_user.id, title=title)
    return ai_schema.AIChatSessionRead.model_validate(session)


async def list_user_sessions(
    db: AsyncSession, current_user: user_model.User
) -> list[ai_schema.AIChatSessionRead]:
    sessions = await ai_repository.list_user_sessions(db, user_id=current_user.id)
    return [ai_schema.AIChatSessionRead.model_validate(s) for s in sessions]


async def get_session_details(
    db: AsyncSession, current_user: user_model.User, session_id: str
) -> ai_schema.AIChatSessionDetail:
    session = await ai_repository.get_session_by_id(db, session_id)
    if not session:
        raise NotFoundException(detail="Chat session not found.")
    if session.user_id != current_user.id:
        raise ForbiddenException(detail="Access denied to this chat session.")
    return ai_schema.AIChatSessionDetail.model_validate(session)


async def list_admin_sessions(
    db: AsyncSession, limit: int = 200
) -> list[ai_schema.AIChatAdminSessionRead]:
    rows = await ai_repository.list_all_sessions(db, limit=limit)
    return [
        ai_schema.AIChatAdminSessionRead(
            **ai_schema.AIChatSessionRead.model_validate(session).model_dump(),
            user=session.user,
            message_count=message_count,
        )
        for session, message_count in rows
    ]


async def get_admin_session_details(
    db: AsyncSession, session_id: str
) -> ai_schema.AIChatAdminSessionDetail:
    session = await ai_repository.get_session_by_id(db, session_id)
    if not session:
        raise NotFoundException(detail="Chat session not found.")
    return ai_schema.AIChatAdminSessionDetail.model_validate(session)


async def delete_chat_session(
    db: AsyncSession, current_user: user_model.User, session_id: str
) -> None:
    session = await ai_repository.get_session_by_id(db, session_id)
    if not session:
        raise NotFoundException(detail="Chat session not found.")
    if session.user_id != current_user.id:
        raise ForbiddenException(detail="Access denied to this chat session.")
    await ai_repository.delete_session(db, session)


async def send_user_message(
    db: AsyncSession,
    current_user: user_model.User,
    session_id: str,
    data: ai_schema.AIChatMessageCreate,
) -> ai_schema.AIChatMessageRead:
    session = await ai_repository.get_session_by_id(db, session_id)
    if not session:
        raise NotFoundException(detail="Chat session not found.")
    if session.user_id != current_user.id:
        raise ForbiddenException(detail="Access denied to this chat session.")

    clean_content = data.content.strip()
    if not clean_content:
        raise BadRequestException(detail="Message content cannot be empty.")

    # 1. Persist User Message
    user_msg = await ai_repository.create_message(
        db, session_id=session_id, role="user", content=clean_content
    )

    # 2. Update Session Title / Updated_at
    await ai_repository.touch_session_title(db, session, clean_content)

    # 3. Load limited recent conversation history
    recent_db_msgs = await ai_repository.get_recent_messages(
        db, session_id=session_id, limit=settings.AI_HISTORY_MESSAGE_LIMIT
    )

    history: list[tuple[str, str]] = []
    for msg in recent_db_msgs:
        if msg.id != user_msg.id:  # Exclude current prompt from history payload
            history.append((msg.role, msg.content))

    # 4. Generate AI Response
    try:
        assistant_reply = await generate_chat_response(
            system_prompt=prompts.SYSTEM_PROMPT,
            history=history,
            user_message=clean_content,
        )
    except AiProviderError as exc:
        if exc.code == "provider_not_configured":
            assistant_reply = prompts.get_unconfigured_response(clean_content)
        else:
            logger.warning("AI provider error: %s. Using automated fallback response.", exc)
            assistant_reply = prompts.get_unconfigured_response(clean_content)
    except Exception as exc:
        logger.warning("Unexpected AI error: %s. Using automated fallback response.", exc)
        assistant_reply = prompts.get_unconfigured_response(clean_content)

    if not assistant_reply or not assistant_reply.strip():
        assistant_reply = prompts.OUT_OF_SCOPE_RESPONSE

    # 5. Persist Assistant Message
    assistant_msg = await ai_repository.create_message(
        db, session_id=session_id, role="assistant", content=assistant_reply
    )

    return ai_schema.AIChatMessageRead.model_validate(assistant_msg)
