from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.features.v1.ai_integration import schema as ai_schema
from app.features.v1.ai_integration import service as ai_service
from app.features.v1.auth.dependencies import get_current_user, require_role
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/ai-integration", tags=["ai-integration"])


@router.get(
    "/admin/sessions",
    response_model=list[ai_schema.AIChatAdminSessionRead],
)
async def list_all_chat_sessions(
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(require_role("admin")),
):
    return await ai_service.list_admin_sessions(db, limit=limit)


@router.get(
    "/admin/sessions/{session_id}",
    response_model=ai_schema.AIChatAdminSessionDetail,
)
async def get_any_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(require_role("admin")),
):
    return await ai_service.get_admin_session_details(db, session_id)


@router.post(
    "/sessions",
    response_model=ai_schema.AIChatSessionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_session(
    data: ai_schema.AIChatSessionCreate | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    title = data.title if data else None
    return await ai_service.create_chat_session(db, current_user, title=title)


@router.get(
    "/sessions",
    response_model=list[ai_schema.AIChatSessionRead],
)
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await ai_service.list_user_sessions(db, current_user)


@router.get(
    "/sessions/{session_id}",
    response_model=ai_schema.AIChatSessionDetail,
)
async def get_chat_session_details(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await ai_service.get_session_details(db, current_user, session_id)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    await ai_service.delete_chat_session(db, current_user, session_id)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ai_schema.AIChatMessageRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("15/minute")
async def send_user_message(
    request: Request,
    session_id: str,
    data: ai_schema.AIChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await ai_service.send_user_message(db, current_user, session_id, data)
