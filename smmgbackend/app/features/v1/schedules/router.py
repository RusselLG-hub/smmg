from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import get_current_user, require_role
from app.features.v1.schedules import schema as schedule_schema
from app.features.v1.schedules import service as schedule_service
from app.features.v1.users import model as user_model

router = APIRouter(tags=["schedules"])


@router.get(
    "/v1/schedules/doctors/{doctor_id}",
    response_model=list[schedule_schema.DoctorScheduleRead],
)
async def list_doctor_schedules(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await schedule_service.list_doctor_schedules(db, doctor_id)


@router.post(
    "/v1/schedules",
    response_model=schedule_schema.DoctorScheduleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("doctor", "staff", "admin"))],
)
async def create_schedule(
    data: schedule_schema.DoctorScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await schedule_service.create_schedule(db, current_user, data)


@router.put(
    "/v1/schedules/{schedule_id}",
    response_model=schedule_schema.DoctorScheduleRead,
    dependencies=[Depends(require_role("doctor", "staff", "admin"))],
)
async def update_schedule(
    schedule_id: str,
    data: schedule_schema.DoctorScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await schedule_service.update_schedule(db, current_user, schedule_id, data)


@router.delete(
    "/v1/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("doctor", "staff", "admin"))],
)
async def delete_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    await schedule_service.delete_schedule(db, current_user, schedule_id)


@router.get(
    "/v1/doctors/{doctor_id}/availability",
    response_model=schedule_schema.AvailabilityResponse,
)
async def get_doctor_availability(
    doctor_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
):
    return await schedule_service.get_doctor_availability(db, doctor_id, date)


@router.get(
    "/v1/doctors/{doctor_id}/availability/month",
    response_model=schedule_schema.MonthlyAvailabilityResponse,
)
async def get_doctor_monthly_availability(
    doctor_id: str,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
):
    return await schedule_service.get_doctor_monthly_availability(
        db, doctor_id, year, month
    )
