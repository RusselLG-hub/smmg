import random
import string
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.features.v1.appointments import repository as appointment_repository
from app.features.v1.appointments import schema as appointment_schema
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.notifications import service as notification_service
from app.features.v1.patients import repository as patient_repository
from app.features.v1.schedules import repository as schedule_repository
from app.features.v1.services import repository as clinic_service_repository
from app.features.v1.users import model as user_model


def _generate_reference() -> str:
    year = datetime.now().year
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"APT-{year}-{random_str}"


def _parse_time(time_str: str) -> time:
    parts = time_str.split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))


async def _validate_slot_against_schedule(
    db: AsyncSession, doctor_id: str, date_str: str, time_str: str
) -> tuple[datetime, int]:
    try:
        req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise BadRequestException(detail="Invalid date format. Expected YYYY-MM-DD.")

    req_time = _parse_time(time_str)
    now_clinic = datetime.now(ZoneInfo("Asia/Manila"))
    today_clinic = now_clinic.date()

    if req_date < today_clinic or (req_date == today_clinic and req_time <= now_clinic.time()):
        raise BadRequestException(detail="Appointment time must be in the future.")

    scheduled_at = datetime.combine(req_date, req_time, tzinfo=timezone.utc)

    # Check override
    override = await schedule_repository.get_override_by_date(db, doctor_id, date_str)
    if override and not override.is_available:
        raise BadRequestException(detail="Doctor is not available on this date.")

    # An available date override replaces the recurring weekly schedule.
    day_of_week = req_date.weekday()
    if override and override.is_available and override.start_time and override.end_time:
        schedule_ranges = [(override.start_time, override.end_time)]
    else:
        schedules = await schedule_repository.get_by_doctor_and_day(
            db, doctor_id, day_of_week, active_only=True
        )
        schedule_ranges = [(schedule.start_time, schedule.end_time) for schedule in schedules]

    if not schedule_ranges:
        raise BadRequestException(detail="Doctor has no active working schedule for this day.")

    slot_valid = False
    slot_duration = 30

    for start_time, end_time in schedule_ranges:
        start_t = _parse_time(start_time)
        end_t = _parse_time(end_time)
        duration = timedelta(minutes=30)

        curr = datetime.combine(req_date, start_t, tzinfo=timezone.utc)
        end_dt = datetime.combine(req_date, end_t, tzinfo=timezone.utc)

        while curr + duration <= end_dt:
            if curr.time() == req_time:
                slot_valid = True
                slot_duration = 30
                break
            curr += duration
        if slot_valid:
            break

    if not slot_valid:
        raise BadRequestException(detail="Requested time does not match doctor's working slots.")

    return scheduled_at, slot_duration


async def create_appointment(
    db: AsyncSession,
    current_user: user_model.User,
    data: appointment_schema.AppointmentCreate,
) -> appointment_schema.AppointmentRead:
    # Resolve PatientProfile
    if current_user.role == "patient":
        patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
        if not patient_prof:
            raise BadRequestException(detail="Patient profile not found. Please complete your profile first.")
        patient_profile_id = patient_prof.id
    else:
        raise ForbiddenException(detail="Only patients can book appointments directly.")

    # Validate Doctor
    doctor = await doctor_repository.get_by_id(db, data.doctor_profile_id)
    if not doctor or not doctor.is_active:
        raise NotFoundException(detail="Doctor not found or inactive.")

    # Validate Service if provided
    srv_name = None
    if data.service_id:
        srv = await clinic_service_repository.get_by_id(db, data.service_id)
        if not srv or not srv.is_active:
            raise NotFoundException(detail="Clinic service not found or inactive.")
        if srv.specialty_id and srv.specialty_id != doctor.specialty_id:
            raise BadRequestException(
                detail="The selected doctor does not provide this clinic service."
            )
        srv_name = srv.name

    # Schedule & Slot Validation
    scheduled_at, slot_duration = await _validate_slot_against_schedule(
        db, data.doctor_profile_id, data.date, data.time
    )

    # Active conflict check
    has_conflict = await appointment_repository.check_active_conflict(
        db, data.doctor_profile_id, scheduled_at
    )
    if has_conflict:
        raise ConflictException(
            detail="That time slot is no longer available. Please choose another time."
        )

    # Generate unique reference
    reference = _generate_reference()
    while await appointment_repository.get_by_reference(db, reference):
        reference = _generate_reference()

    try:
        appt = await appointment_repository.create_appointment(
            db=db,
            patient_profile_id=patient_profile_id,
            doctor_profile_id=data.doctor_profile_id,
            service_id=data.service_id,
            reference=reference,
            scheduled_at=scheduled_at,
            slot_duration=slot_duration,
            reason=data.reason,
            status="pending",
        )

        # Trigger booking email notification (non-blocking side-effect)
        try:
            specialty_name = doctor.specialty.name if doctor.specialty else None
            notification_service.send_booking_notification(
                patient_email=current_user.email,
                patient_name=current_user.name,
                reference=reference,
                doctor_name=doctor.user.name,
                specialty_name=specialty_name,
                service_name=srv_name,
                date_str=data.date,
                time_str=data.time,
            )
        except Exception:
            pass

        return appointment_schema.AppointmentRead.model_validate(appt)
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="That time slot has just been booked by another user. Please choose another time."
        )


async def cancel_appointment(
    db: AsyncSession,
    current_user: user_model.User,
    appointment_id: str,
    data: appointment_schema.AppointmentCancel,
) -> appointment_schema.AppointmentRead:
    appt = await appointment_repository.get_by_id(db, appointment_id)
    if not appt:
        raise NotFoundException(detail="Appointment not found.")

    now_utc = datetime.now(timezone.utc)

    if current_user.role == "patient":
        patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
        if not patient_prof or appt.patient_profile_id != patient_prof.id:
            raise ForbiddenException(detail="Patients can only cancel their own appointments.")

        if appt.status == "confirmed":
            raise BadRequestException(
                detail="Confirmed appointments cannot be cancelled by patients. Please contact clinic staff directly."
            )

        if appt.scheduled_at - now_utc < timedelta(hours=24):
            raise BadRequestException(
                detail="Appointments cannot be cancelled by patients within 24 hours of the scheduled time. Please contact clinic staff."
            )
    elif current_user.role == "doctor":
        my_doctor = await doctor_repository.get_by_user_id(db, current_user.id)
        if not my_doctor or my_doctor.id != appt.doctor_profile_id:
            raise ForbiddenException(detail="Doctors can only cancel their assigned appointments.")
    elif current_user.role not in ["staff", "admin"]:
        raise ForbiddenException(detail="You are not allowed to cancel this appointment.")

    if appt.status in ["cancelled", "completed"]:
        raise BadRequestException(detail=f"Cannot cancel appointment with status '{appt.status}'.")

    updated = await appointment_repository.update_status(
        db, appointment_id, status="cancelled", cancellation_reason=data.cancellation_reason
    )

    # Trigger cancellation notification
    try:
        notification_service.send_cancellation_notification(
            patient_email=updated.patient.user.email,
            patient_name=updated.patient.user.name,
            reference=updated.appointment_reference,
            doctor_name=updated.doctor.user.name,
            date_str=updated.scheduled_at.strftime("%Y-%m-%d"),
            time_str=updated.scheduled_at.strftime("%H:%M"),
            cancellation_reason=data.cancellation_reason,
        )
    except Exception:
        pass

    return appointment_schema.AppointmentRead.model_validate(updated)


async def reschedule_appointment(
    db: AsyncSession,
    current_user: user_model.User,
    appointment_id: str,
    data: appointment_schema.AppointmentReschedule,
) -> appointment_schema.AppointmentRead:
    appt = await appointment_repository.get_by_id(db, appointment_id)
    if not appt:
        raise NotFoundException(detail="Appointment not found.")

    now_utc = datetime.now(timezone.utc)

    if current_user.role == "patient":
        patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
        if not patient_prof or appt.patient_profile_id != patient_prof.id:
            raise ForbiddenException(detail="Patients can only reschedule their own appointments.")

        if appt.status == "confirmed":
            raise BadRequestException(
                detail="Confirmed appointments cannot be rescheduled by patients. Please contact clinic staff directly."
            )

        if appt.scheduled_at - now_utc < timedelta(hours=24):
            raise BadRequestException(
                detail="Appointments cannot be rescheduled by patients within 24 hours of the scheduled time."
            )
    elif current_user.role not in ["staff", "admin"]:
        raise ForbiddenException(detail="Only patients, staff, and admins can reschedule appointments.")

    if appt.status in ["cancelled", "completed"]:
        raise BadRequestException(detail=f"Cannot reschedule appointment with status '{appt.status}'.")

    old_date_str = appt.scheduled_at.strftime("%Y-%m-%d %H:%M")

    new_scheduled_at, _ = await _validate_slot_against_schedule(
        db, appt.doctor_profile_id, data.date, data.time
    )

    has_conflict = await appointment_repository.check_active_conflict(
        db, appt.doctor_profile_id, new_scheduled_at, exclude_id=appt.id
    )
    if has_conflict:
        raise ConflictException(
            detail="The new time slot is no longer available. Please choose another time."
        )

    try:
        new_status = "pending" if current_user.role == "patient" else appt.status
        updated = await appointment_repository.reschedule(
            db, appointment_id, new_scheduled_at, new_status=new_status
        )
        # Reset reminder state so new time receives reminder
        updated.reminder_sent_at = None
        await db.commit()
        await db.refresh(updated)

        # Trigger reschedule notification
        try:
            notification_service.send_reschedule_notification(
                patient_email=updated.patient.user.email,
                patient_name=updated.patient.user.name,
                reference=updated.appointment_reference,
                doctor_name=updated.doctor.user.name,
                old_date_str=old_date_str,
                new_date_str=data.date,
                new_time_str=data.time,
                pending_confirmation=current_user.role == "patient",
            )
        except Exception:
            pass

        return appointment_schema.AppointmentRead.model_validate(updated)
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="The new time slot has just been booked by another user."
        )


async def update_appointment_status(
    db: AsyncSession,
    current_user: user_model.User,
    appointment_id: str,
    data: appointment_schema.AppointmentStatusUpdate,
) -> appointment_schema.AppointmentRead:
    appt = await appointment_repository.get_by_id(db, appointment_id)
    if not appt:
        raise NotFoundException(detail="Appointment not found.")

    if current_user.role == "doctor":
        my_doctor = await doctor_repository.get_by_user_id(db, current_user.id)
        if not my_doctor or my_doctor.id != appt.doctor_profile_id:
            raise ForbiddenException(detail="Doctors can only update their assigned appointments.")
        valid_transitions = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["completed", "cancelled"],
        }
    elif current_user.role in ["staff", "admin"]:
        valid_transitions = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["cancelled"],
        }
    else:
        raise ForbiddenException(detail="You are not allowed to update appointment status.")

    allowed_next = valid_transitions.get(appt.status, [])
    if data.status not in allowed_next:
        raise BadRequestException(
            detail=f"Cannot transition appointment status from '{appt.status}' to '{data.status}'."
        )

    prev_status = appt.status
    updated = await appointment_repository.update_status(db, appointment_id, data.status)

    # Trigger notifications based on status change
    try:
        if prev_status == "pending" and data.status == "confirmed":
            notification_service.send_status_confirmed_notification(
                patient_email=updated.patient.user.email,
                patient_name=updated.patient.user.name,
                reference=updated.appointment_reference,
                doctor_name=updated.doctor.user.name,
                date_str=updated.scheduled_at.strftime("%Y-%m-%d"),
                time_str=updated.scheduled_at.strftime("%H:%M"),
            )
        elif data.status == "cancelled":
            notification_service.send_cancellation_notification(
                patient_email=updated.patient.user.email,
                patient_name=updated.patient.user.name,
                reference=updated.appointment_reference,
                doctor_name=updated.doctor.user.name,
                date_str=updated.scheduled_at.strftime("%Y-%m-%d"),
                time_str=updated.scheduled_at.strftime("%H:%M"),
            )
    except Exception:
        pass

    return appointment_schema.AppointmentRead.model_validate(updated)


async def list_my_appointments(
    db: AsyncSession, current_user: user_model.User, type_filter: str = "all"
) -> list[appointment_schema.AppointmentRead]:
    patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
    if not patient_prof:
        return []

    upcoming_only = type_filter == "upcoming"
    past_only = type_filter == "past"

    items = await appointment_repository.get_patient_appointments(
        db, patient_prof.id, upcoming_only=upcoming_only, past_only=past_only
    )
    return [appointment_schema.AppointmentRead.model_validate(i) for i in items]


async def list_doctor_appointments(
    db: AsyncSession,
    current_user: user_model.User,
    date_str: str | None = None,
    status: str | None = None,
) -> list[appointment_schema.AppointmentRead]:
    doctor_prof = await doctor_repository.get_by_user_id(db, current_user.id)
    if not doctor_prof:
        return []

    items = await appointment_repository.get_doctor_appointments(
        db, doctor_prof.id, date_str=date_str, status=status
    )
    return [appointment_schema.AppointmentRead.model_validate(i) for i in items]


async def list_admin_appointments(
    db: AsyncSession,
    doctor_id: str | None = None,
    patient_id: str | None = None,
    status: str | None = None,
    date_str: str | None = None,
) -> list[appointment_schema.AppointmentRead]:
    items = await appointment_repository.list_appointments(
        db, doctor_id=doctor_id, patient_id=patient_id, status=status, date_str=date_str
    )
    return [appointment_schema.AppointmentRead.model_validate(i) for i in items]


async def get_appointment_details(
    db: AsyncSession, current_user: user_model.User, appointment_id: str
) -> appointment_schema.AppointmentRead:
    appt = await appointment_repository.get_by_id(db, appointment_id)
    if not appt:
        raise NotFoundException(detail="Appointment not found.")

    if current_user.role == "patient":
        patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
        if not patient_prof or appt.patient_profile_id != patient_prof.id:
            raise ForbiddenException(detail="Access denied to this appointment.")

    elif current_user.role == "doctor":
        doctor_prof = await doctor_repository.get_by_user_id(db, current_user.id)
        if not doctor_prof or appt.doctor_profile_id != doctor_prof.id:
            raise ForbiddenException(detail="Access denied to this appointment.")

    return appointment_schema.AppointmentRead.model_validate(appt)
