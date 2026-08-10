from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.schedules.model import DoctorSchedule, DoctorScheduleOverride
from app.features.v1.schedules.schema import (
    DoctorScheduleCreate,
    DoctorScheduleOverrideCreate,
    DoctorScheduleUpdate,
)


async def get_by_doctor_id(
    db: AsyncSession, doctor_profile_id: str, active_only: bool = False
) -> list[DoctorSchedule]:
    stmt = select(DoctorSchedule).where(
        DoctorSchedule.doctor_profile_id == doctor_profile_id
    )
    if active_only:
        stmt = stmt.where(DoctorSchedule.is_active == True)
    stmt = stmt.order_by(DoctorSchedule.day_of_week.asc(), DoctorSchedule.start_time.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, schedule_id: str) -> DoctorSchedule | None:
    result = await db.execute(
        select(DoctorSchedule).where(DoctorSchedule.id == schedule_id)
    )
    return result.scalar_one_or_none()


async def get_by_doctor_and_day(
    db: AsyncSession, doctor_profile_id: str, day_of_week: int, active_only: bool = True
) -> list[DoctorSchedule]:
    stmt = select(DoctorSchedule).where(
        DoctorSchedule.doctor_profile_id == doctor_profile_id,
        DoctorSchedule.day_of_week == day_of_week,
    )
    if active_only:
        stmt = stmt.where(DoctorSchedule.is_active == True)
    stmt = stmt.order_by(DoctorSchedule.start_time.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def check_overlap(
    db: AsyncSession,
    doctor_profile_id: str,
    day_of_week: int,
    start_time: str,
    end_time: str,
    exclude_id: str | None = None,
) -> bool:
    stmt = select(DoctorSchedule).where(
        DoctorSchedule.doctor_profile_id == doctor_profile_id,
        DoctorSchedule.day_of_week == day_of_week,
        DoctorSchedule.is_active == True,
        DoctorSchedule.start_time < end_time,
        DoctorSchedule.end_time > start_time,
    )
    if exclude_id:
        stmt = stmt.where(DoctorSchedule.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalars().first() is not None


async def create_schedule(
    db: AsyncSession, data: DoctorScheduleCreate, doctor_profile_id: str
) -> DoctorSchedule:
    schedule = DoctorSchedule(
        doctor_profile_id=doctor_profile_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration_minutes=data.slot_duration_minutes,
        is_active=data.is_active,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def update_schedule(
    db: AsyncSession, schedule_id: str, data: DoctorScheduleUpdate
) -> DoctorSchedule | None:
    schedule = await get_by_id(db, schedule_id)
    if not schedule:
        return None

    if data.day_of_week is not None:
        schedule.day_of_week = data.day_of_week
    if data.start_time is not None:
        schedule.start_time = data.start_time
    if data.end_time is not None:
        schedule.end_time = data.end_time
    if data.slot_duration_minutes is not None:
        schedule.slot_duration_minutes = data.slot_duration_minutes
    if data.is_active is not None:
        schedule.is_active = data.is_active

    await db.commit()
    await db.refresh(schedule)
    return schedule


async def delete_schedule(db: AsyncSession, schedule_id: str) -> bool:
    schedule = await get_by_id(db, schedule_id)
    if not schedule:
        return False
    await db.delete(schedule)
    await db.commit()
    return True


async def get_override_by_date(
    db: AsyncSession, doctor_profile_id: str, date_str: str
) -> DoctorScheduleOverride | None:
    result = await db.execute(
        select(DoctorScheduleOverride).where(
            DoctorScheduleOverride.doctor_profile_id == doctor_profile_id,
            DoctorScheduleOverride.date == date_str,
        )
    )
    return result.scalar_one_or_none()


async def create_override(
    db: AsyncSession, data: DoctorScheduleOverrideCreate, doctor_profile_id: str
) -> DoctorScheduleOverride:
    override = DoctorScheduleOverride(
        doctor_profile_id=doctor_profile_id,
        date=data.date,
        is_available=data.is_available,
        start_time=data.start_time,
        end_time=data.end_time,
        reason=data.reason,
    )
    db.add(override)
    await db.commit()
    await db.refresh(override)
    return override
