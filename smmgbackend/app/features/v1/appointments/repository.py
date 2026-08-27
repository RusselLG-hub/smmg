from datetime import date, datetime, time, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.appointments.model import Appointment

BLOCKING_STATUSES = ["pending", "confirmed"]


async def get_by_id(db: AsyncSession, appointment_id: str) -> Appointment | None:
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    return result.scalar_one_or_none()


async def get_by_reference(db: AsyncSession, reference: str) -> Appointment | None:
    result = await db.execute(
        select(Appointment).where(Appointment.appointment_reference == reference)
    )
    return result.scalar_one_or_none()


async def get_patient_appointments(
    db: AsyncSession,
    patient_profile_id: str,
    upcoming_only: bool = False,
    past_only: bool = False,
) -> list[Appointment]:
    now = datetime.now(timezone.utc)
    stmt = select(Appointment).where(
        Appointment.patient_profile_id == patient_profile_id
    )

    if upcoming_only:
        stmt = stmt.where(
            Appointment.scheduled_at >= now,
            Appointment.status.in_(BLOCKING_STATUSES),
        ).order_by(Appointment.scheduled_at.asc())
    elif past_only:
        stmt = stmt.where(
            (Appointment.scheduled_at < now) | (Appointment.status == "cancelled") | (Appointment.status == "completed")
        ).order_by(Appointment.scheduled_at.desc())
    else:
        stmt = stmt.order_by(Appointment.scheduled_at.desc())

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_doctor_appointments(
    db: AsyncSession,
    doctor_profile_id: str,
    date_str: str | None = None,
    status: str | None = None,
) -> list[Appointment]:
    stmt = select(Appointment).where(
        Appointment.doctor_profile_id == doctor_profile_id
    )

    if status:
        stmt = stmt.where(Appointment.status == status)

    if date_str:
        req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_dt = datetime.combine(req_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(req_date, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(Appointment.scheduled_at >= start_dt, Appointment.scheduled_at <= end_dt)

    stmt = stmt.order_by(Appointment.scheduled_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_appointments(
    db: AsyncSession,
    doctor_id: str | None = None,
    patient_id: str | None = None,
    status: str | None = None,
    date_str: str | None = None,
) -> list[Appointment]:
    stmt = select(Appointment)

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)
    if patient_id:
        stmt = stmt.where(Appointment.patient_profile_id == patient_id)
    if status:
        stmt = stmt.where(Appointment.status == status)
    if date_str:
        req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_dt = datetime.combine(req_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(req_date, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(Appointment.scheduled_at >= start_dt, Appointment.scheduled_at <= end_dt)

    stmt = stmt.order_by(Appointment.scheduled_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_active_appointments_for_doctor_date(
    db: AsyncSession, doctor_profile_id: str, date_obj: date
) -> list[Appointment]:
    start_dt = datetime.combine(date_obj, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(date_obj, time.max, tzinfo=timezone.utc)

    stmt = select(Appointment).where(
        Appointment.doctor_profile_id == doctor_profile_id,
        Appointment.status.in_(BLOCKING_STATUSES),
        Appointment.scheduled_at >= start_dt,
        Appointment.scheduled_at <= end_dt,
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def check_active_conflict(
    db: AsyncSession,
    doctor_profile_id: str,
    scheduled_at: datetime,
    exclude_id: str | None = None,
) -> bool:
    stmt = select(Appointment).where(
        Appointment.doctor_profile_id == doctor_profile_id,
        Appointment.scheduled_at == scheduled_at,
        Appointment.status.in_(BLOCKING_STATUSES),
    )
    if exclude_id:
        stmt = stmt.where(Appointment.id != exclude_id)

    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def create_appointment(
    db: AsyncSession,
    patient_profile_id: str,
    doctor_profile_id: str,
    service_id: str | None,
    reference: str,
    scheduled_at: datetime,
    slot_duration: int = 30,
    reason: str | None = None,
    status: str = "pending",
) -> Appointment:
    appointment = Appointment(
        appointment_reference=reference,
        patient_profile_id=patient_profile_id,
        doctor_profile_id=doctor_profile_id,
        service_id=service_id,
        scheduled_at=scheduled_at,
        slot_duration_minutes=slot_duration,
        status=status,
        reason=reason,
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def update_status(
    db: AsyncSession,
    appointment_id: str,
    status: str,
    cancellation_reason: str | None = None,
) -> Appointment | None:
    appt = await get_by_id(db, appointment_id)
    if not appt:
        return None

    appt.status = status
    if cancellation_reason is not None:
        appt.cancellation_reason = cancellation_reason

    await db.commit()
    await db.refresh(appt)
    return appt


async def reschedule(
    db: AsyncSession,
    appointment_id: str,
    new_scheduled_at: datetime,
    new_status: str | None = None,
) -> Appointment | None:
    appt = await get_by_id(db, appointment_id)
    if not appt:
        return None

    appt.scheduled_at = new_scheduled_at
    if new_status is not None:
        appt.status = new_status
    await db.commit()
    await db.refresh(appt)
    return appt
