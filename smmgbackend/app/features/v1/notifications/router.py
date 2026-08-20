from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import get_current_user
from app.features.v1.notifications import schema, service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])


@router.get("", response_model=list[schema.InAppNotification])
async def list_notifications(
    limit: int = Query(default=12, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
) -> list[schema.InAppNotification]:
    return await service.get_in_app_notifications(db, current_user, limit)

