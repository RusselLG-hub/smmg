from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.users import schema as user_schema
from app.features.v1.users import service as user_service

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.get(
    "",
    response_model=list[user_schema.UserRead],
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def list_users(
    role: str | None = Query(None, description="Filter by role: patient, doctor, staff, admin"),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.list_users(db, role=role)


@router.post(
    "/staff",
    response_model=user_schema.UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_staff_user(
    data: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.create_staff_user(db, data)


@router.patch(
    "/{user_id}/toggle-active",
    response_model=user_schema.UserRead,
    dependencies=[Depends(require_role("admin"))],
)
async def toggle_user_active(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.toggle_user_active(db, user_id)
