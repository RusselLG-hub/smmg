from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.doctors import schema as doctor_schema
from app.features.v1.doctors import service as doctor_service

from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/doctors", tags=["doctors"])


@router.get("", response_model=list[doctor_schema.DoctorRead])
async def list_doctors(
    active_only: bool = Query(False),
    specialty_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.list_doctors(
        db, active_only=active_only, specialty_id=specialty_id
    )


@router.get("/me", response_model=doctor_schema.DoctorRead)
async def get_my_doctor_profile(
    current_user: user_model.User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.get_doctor_by_user_id(db, current_user.id)


@router.put("/me", response_model=doctor_schema.DoctorRead)
async def update_my_doctor_profile(
    data: doctor_schema.DoctorUpdate,
    current_user: user_model.User = Depends(require_role("doctor")),
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.update_my_doctor_profile(db, current_user.id, data)


@router.get("/{doctor_id}", response_model=doctor_schema.DoctorRead)
async def get_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.get_doctor(db, doctor_id)


@router.post(
    "",
    response_model=doctor_schema.DoctorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def create_doctor(
    data: doctor_schema.DoctorCreate,
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.create_doctor(db, data)


@router.put(
    "/{doctor_id}",
    response_model=doctor_schema.DoctorRead,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def update_doctor(
    doctor_id: str,
    data: doctor_schema.DoctorUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.update_doctor(db, doctor_id, data)


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
):
    await doctor_service.delete_doctor(db, doctor_id)
