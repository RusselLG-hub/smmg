from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.specialties import schema as specialty_schema
from app.features.v1.specialties import service as specialty_service

router = APIRouter(prefix="/v1/specialties", tags=["specialties"])


@router.get("", response_model=list[specialty_schema.SpecialtyRead])
async def list_specialties(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    return await specialty_service.list_specialties(db, active_only=active_only)


@router.get("/{specialty_id}", response_model=specialty_schema.SpecialtyRead)
async def get_specialty(
    specialty_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await specialty_service.get_specialty(db, specialty_id)


@router.post(
    "",
    response_model=specialty_schema.SpecialtyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def create_specialty(
    data: specialty_schema.SpecialtyCreate,
    db: AsyncSession = Depends(get_db),
):
    return await specialty_service.create_specialty(db, data)


@router.put(
    "/{specialty_id}",
    response_model=specialty_schema.SpecialtyRead,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def update_specialty(
    specialty_id: str,
    data: specialty_schema.SpecialtyUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await specialty_service.update_specialty(db, specialty_id, data)


@router.delete(
    "/{specialty_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_specialty(
    specialty_id: str,
    db: AsyncSession = Depends(get_db),
):
    await specialty_service.delete_specialty(db, specialty_id)
