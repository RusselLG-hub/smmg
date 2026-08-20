from datetime import datetime, time, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.features.v1.appointments import repository as appointment_repository
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.schedules import repository as schedule_repository
from app.features.v1.schedules import schema as schedule_schema
from app.features.v1.users import model as user_model


def _parse_time(time_str: str) -> time:
    parts = time_str.split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))


def _format_time(t: time) -> str:
    return t.strftime("%H:%M")


async def list_doctor_schedules(
    db: AsyncSession, doctor_id: str
) -> list[schedule_schema.DoctorScheduleRead]:
    doctor = await doctor_repository.get_by_id(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor profile not found")

    items = await schedule_repository.get_by_doctor_id(db, doctor_profile_id=doctor_id)
    return [schedule_schema.DoctorScheduleRead.model_validate(i) for i in items]


async def create_schedule(
    db: AsyncSession,
    current_user: user_model.User,
    data: schedule_schema.DoctorScheduleCreate,
) -> schedule_schema.DoctorScheduleRead:
    # Resolve target doctor_profile_id
    doctor_id = data.doctor_profile_id

    if current_user.role == "doctor":
        my_doctor = await doctor_repository.get_by_user_id(db, current_user.id)
        if not my_doctor:
            raise ForbiddenException(detail="Doctor profile not found for current user")
        if doctor_id and doctor_id != my_doctor.id:
            raise ForbiddenException(detail="Doctors can only manage their own schedules")
        doctor_id = my_doctor.id
    elif not doctor_id:
        raise BadRequestException(detail="doctor_profile_id is required")

    doctor = await doctor_repository.get_by_id(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor profile not found")

    # Time validation
    if data.start_time >= data.end_time:
        raise BadRequestException(detail="start_time must be strictly before end_time")

    # Overlap validation if active
    if data.is_active:
        has_overlap = await schedule_repository.check_overlap(
            db,
            doctor_profile_id=doctor_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        if has_overlap:
            raise ConflictException(
                detail="Schedule time overlaps with an existing active schedule for this day"
            )

    item = await schedule_repository.create_schedule(db, data, doctor_profile_id=doctor_id)
    return schedule_schema.DoctorScheduleRead.model_validate(item)


async def update_schedule(
    db: AsyncSession,
    current_user: user_model.User,
    schedule_id: str,
    data: schedule_schema.DoctorScheduleUpdate,
) -> schedule_schema.DoctorScheduleRead:
    schedule = await schedule_repository.get_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException(detail="Schedule not found")

    if current_user.role == "doctor":
        my_doctor = await doctor_repository.get_by_user_id(db, current_user.id)
        if not my_doctor or my_doctor.id != schedule.doctor_profile_id:
            raise ForbiddenException(detail="Doctors can only manage their own schedules")

    new_day = data.day_of_week if data.day_of_week is not None else schedule.day_of_week
    new_start = data.start_time if data.start_time is not None else schedule.start_time
    new_end = data.end_time if data.end_time is not None else schedule.end_time
    new_active = data.is_active if data.is_active is not None else schedule.is_active

    if new_start >= new_end:
        raise BadRequestException(detail="start_time must be strictly before end_time")

    if new_active:
        has_overlap = await schedule_repository.check_overlap(
            db,
            doctor_profile_id=schedule.doctor_profile_id,
            day_of_week=new_day,
            start_time=new_start,
            end_time=new_end,
            exclude_id=schedule.id,
        )
        if has_overlap:
            raise ConflictException(
                detail="Schedule time overlaps with an existing active schedule for this day"
            )

    updated = await schedule_repository.update_schedule(db, schedule_id, data)
    if not updated:
        raise NotFoundException(detail="Schedule not found")

    return schedule_schema.DoctorScheduleRead.model_validate(updated)


async def delete_schedule(
    db: AsyncSession, current_user: user_model.User, schedule_id: str
) -> None:
    schedule = await schedule_repository.get_by_id(db, schedule_id)
    if not schedule:
        raise NotFoundException(detail="Schedule not found")

    if current_user.role == "doctor":
        my_doctor = await doctor_repository.get_by_user_id(db, current_user.id)
        if not my_doctor or my_doctor.id != schedule.doctor_profile_id:
            raise ForbiddenException(detail="Doctors can only manage their own schedules")

    await schedule_repository.delete_schedule(db, schedule_id)


async def get_doctor_availability(
    db: AsyncSession, doctor_id: str, date_str: str
) -> schedule_schema.AvailabilityResponse:
    try:
        req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise BadRequestException(detail="Invalid date format. Expected YYYY-MM-DD.")

    now_utc = datetime.now(timezone.utc)
    today_utc = now_utc.date()

    day_of_week = req_date.weekday()  # 0=Monday, 6=Sunday

    if req_date < today_utc:
        return schedule_schema.AvailabilityResponse(
            doctor_id=doctor_id,
            date=date_str,
            day_of_week=day_of_week,
            is_working_day=False,
            slots=[],
        )

    doctor = await doctor_repository.get_by_id(db, doctor_id)
    if not doctor or not doctor.is_active:
        raise NotFoundException(detail="Doctor not found or inactive")

    # Check date override
    override = await schedule_repository.get_override_by_date(db, doctor_id, date_str)
    if override and not override.is_available:
        return schedule_schema.AvailabilityResponse(
            doctor_id=doctor_id,
            date=date_str,
            day_of_week=day_of_week,
            is_working_day=False,
            slots=[],
        )

    schedules: list[schedule_schema.DoctorScheduleRead] = []
    if override and override.is_available and override.start_time and override.end_time:
        schedules = [
            schedule_schema.DoctorScheduleRead(
                id=override.id,
                doctor_profile_id=override.doctor_profile_id,
                day_of_week=day_of_week,
                start_time=override.start_time,
                end_time=override.end_time,
                slot_duration_minutes=override.slot_duration_minutes or 30,
                is_active=True,
                created_at=override.created_at,
                updated_at=override.updated_at,
            )
        ]
    else:
        db_schedules = await schedule_repository.get_by_doctor_and_day(
            db, doctor_id, day_of_week, active_only=True
        )
        schedules = [schedule_schema.DoctorScheduleRead.model_validate(s) for s in db_schedules]

    if not schedules:
        return schedule_schema.AvailabilityResponse(
            doctor_id=doctor_id,
            date=date_str,
            day_of_week=day_of_week,
            is_working_day=False,
            slots=[],
        )

    # Query active appointments (pending / confirmed) to filter out occupied slots
    active_appts = await appointment_repository.get_active_appointments_for_doctor_date(
        db, doctor_id, req_date
    )
    occupied_slot_starts = set(
        a.scheduled_at.strftime("%H:%M") for a in active_appts
    )

    all_slots: list[schedule_schema.TimeSlot] = []

    for sch in schedules:
        start_t = _parse_time(sch.start_time)
        end_t = _parse_time(sch.end_time)
        duration = timedelta(minutes=sch.slot_duration_minutes)

        curr_datetime = datetime.combine(req_date, start_t, tzinfo=timezone.utc)
        end_datetime = datetime.combine(req_date, end_t, tzinfo=timezone.utc)

        while curr_datetime + duration <= end_datetime:
            slot_start_str = _format_time(curr_datetime.time())
            slot_end_str = _format_time((curr_datetime + duration).time())

            # Filter out past slots for today AND occupied active appointment slots
            is_valid_time = True
            if req_date == today_utc and curr_datetime <= now_utc:
                is_valid_time = False

            if is_valid_time and slot_start_str not in occupied_slot_starts:
                all_slots.append(
                    schedule_schema.TimeSlot(
                        start_time=slot_start_str,
                        end_time=slot_end_str,
                        is_available=True,
                    )
                )

            curr_datetime += duration

    return schedule_schema.AvailabilityResponse(
        doctor_id=doctor_id,
        date=date_str,
        day_of_week=day_of_week,
        is_working_day=len(all_slots) > 0,
        slots=all_slots,
    )
