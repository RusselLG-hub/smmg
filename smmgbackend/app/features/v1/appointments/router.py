from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.appointments import schema as appointment_schema
from app.features.v1.appointments import service as appointment_service
from app.features.v1.auth.dependencies import get_current_user, require_role
from app.features.v1.users import model as user_model

router = APIRouter(tags=["appointments"])


@router.post(
    "/v1/appointments",
    response_model=appointment_schema.AppointmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("patient"))],
)
async def create_appointment(
    data: appointment_schema.AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.create_appointment(db, current_user, data)


@router.get(
    "/v1/appointments/me",
    response_model=list[appointment_schema.AppointmentRead],
    dependencies=[Depends(require_role("patient"))],
)
async def list_my_appointments(
    type: str = Query("all", description="Filter type: all, upcoming, past"),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.list_my_appointments(db, current_user, type)


@router.get(
    "/v1/appointments/doctor/me",
    response_model=list[appointment_schema.AppointmentRead],
    dependencies=[Depends(require_role("doctor"))],
)
async def list_doctor_appointments(
    date: str | None = Query(None, description="Filter date YYYY-MM-DD"),
    status: str | None = Query(None, description="Filter status"),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.list_doctor_appointments(db, current_user, date, status)


@router.get(
    "/v1/appointments",
    response_model=list[appointment_schema.AppointmentRead],
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def list_admin_appointments(
    doctor_id: str | None = Query(None),
    patient_id: str | None = Query(None),
    status: str | None = Query(None),
    date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await appointment_service.list_admin_appointments(
        db, doctor_id=doctor_id, patient_id=patient_id, status=status, date_str=date
    )


@router.get(
    "/v1/appointments/{appointment_id}",
    response_model=appointment_schema.AppointmentRead,
)
async def get_appointment_details(
    appointment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.get_appointment_details(db, current_user, appointment_id)


@router.patch(
    "/v1/appointments/{appointment_id}/cancel",
    response_model=appointment_schema.AppointmentRead,
)
async def cancel_appointment(
    appointment_id: str,
    data: appointment_schema.AppointmentCancel,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.cancel_appointment(db, current_user, appointment_id, data)


@router.patch(
    "/v1/appointments/{appointment_id}/reschedule",
    response_model=appointment_schema.AppointmentRead,
)
async def reschedule_appointment(
    appointment_id: str,
    data: appointment_schema.AppointmentReschedule,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.reschedule_appointment(
        db, current_user, appointment_id, data
    )


@router.patch(
    "/v1/appointments/{appointment_id}/status",
    response_model=appointment_schema.AppointmentRead,
    dependencies=[Depends(require_role("doctor", "staff", "admin"))],
)
async def update_appointment_status(
    appointment_id: str,
    data: appointment_schema.AppointmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await appointment_service.update_appointment_status(
        db, current_user, appointment_id, data
    )
