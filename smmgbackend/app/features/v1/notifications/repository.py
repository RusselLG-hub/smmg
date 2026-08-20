from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.v1.appointments.model import Appointment
from app.features.v1.doctors.model import DoctorProfile
from app.features.v1.patients.model import PatientProfile


async def list_for_user(
    db: AsyncSession,
    *,
    user_id: str,
    role: str,
    limit: int = 12,
) -> list[Appointment]:
    stmt = (
        select(Appointment)
        .options(
            selectinload(Appointment.patient).selectinload(PatientProfile.user),
            selectinload(Appointment.doctor).selectinload(DoctorProfile.user),
            selectinload(Appointment.service),
        )
        .order_by(Appointment.updated_at.desc())
        .limit(limit)
    )

    if role == "patient":
        stmt = stmt.join(Appointment.patient).where(PatientProfile.user_id == user_id)
    elif role == "doctor":
        stmt = stmt.join(Appointment.doctor).where(DoctorProfile.user_id == user_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())

