from datetime import datetime, time, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.features.v1.appointments import model as appt_model
from app.features.v1.appointments import repository as appt_repository
from app.features.v1.appointments import schema as appt_schema
from app.features.v1.dashboard import schema as db_schema
from app.features.v1.doctors import model as doctor_model
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.patients import repository as patient_repository
from app.features.v1.schedules import model as schedule_model
from app.features.v1.services import model as service_model
from app.features.v1.specialties import model as specialty_model
from app.features.v1.users import model as user_model


async def get_patient_dashboard(
    db: AsyncSession, current_user: user_model.User
) -> db_schema.PatientDashboardSummary:
    patient_prof = await patient_repository.get_by_user_id(db, current_user.id)
    if not patient_prof:
        return db_schema.PatientDashboardSummary(
            upcoming_appointment=None, upcoming_count=0, completed_count=0
        )

    now = datetime.now(timezone.utc)

    # Upcoming count
    q_up_count = select(func.count(appt_model.Appointment.id)).where(
        appt_model.Appointment.patient_profile_id == patient_prof.id,
        appt_model.Appointment.scheduled_at >= now,
        appt_model.Appointment.status.in_(["pending", "confirmed"]),
    )
    up_count = (await db.execute(q_up_count)).scalar() or 0

    # Completed count
    q_comp_count = select(func.count(appt_model.Appointment.id)).where(
        appt_model.Appointment.patient_profile_id == patient_prof.id,
        appt_model.Appointment.status == "completed",
    )
    comp_count = (await db.execute(q_comp_count)).scalar() or 0

    # Next upcoming appointment
    q_next = (
        select(appt_model.Appointment)
        .where(
            appt_model.Appointment.patient_profile_id == patient_prof.id,
            appt_model.Appointment.scheduled_at >= now,
            appt_model.Appointment.status.in_(["pending", "confirmed"]),
        )
        .order_by(appt_model.Appointment.scheduled_at.asc())
        .limit(1)
    )
    next_appt = (await db.execute(q_next)).scalar_one_or_none()
    next_schema = (
        appt_schema.AppointmentRead.model_validate(next_appt) if next_appt else None
    )

    return db_schema.PatientDashboardSummary(
        upcoming_appointment=next_schema,
        upcoming_count=up_count,
        completed_count=comp_count,
    )


async def get_doctor_dashboard(
    db: AsyncSession, current_user: user_model.User
) -> db_schema.DoctorDashboardSummary:
    doctor_prof = await doctor_repository.get_by_user_id(db, current_user.id)
    if not doctor_prof:
        raise NotFoundException(detail="Doctor profile not found")

    now = datetime.now(timezone.utc)
    today_date = now.date()
    start_today = datetime.combine(today_date, time.min, tzinfo=timezone.utc)
    end_today = datetime.combine(today_date, time.max, tzinfo=timezone.utc)

    # Today's appointments list & count
    today_appts = await appt_repository.get_doctor_appointments(
        db, doctor_prof.id, date_str=today_date.strftime("%Y-%m-%d")
    )
    today_count = len(today_appts)

    # Upcoming count
    q_up_count = select(func.count(appt_model.Appointment.id)).where(
        appt_model.Appointment.doctor_profile_id == doctor_prof.id,
        appt_model.Appointment.scheduled_at >= now,
        appt_model.Appointment.status.in_(["pending", "confirmed"]),
    )
    upcoming_count = (await db.execute(q_up_count)).scalar() or 0

    # Schedule count
    q_sch_count = select(func.count(schedule_model.DoctorSchedule.id)).where(
        schedule_model.DoctorSchedule.doctor_profile_id == doctor_prof.id,
        schedule_model.DoctorSchedule.is_active == True,
    )
    sch_count = (await db.execute(q_sch_count)).scalar() or 0

    return db_schema.DoctorDashboardSummary(
        today_count=today_count,
        upcoming_count=upcoming_count,
        today_appointments=[
            appt_schema.AppointmentRead.model_validate(a) for a in today_appts
        ],
        schedule_count=sch_count,
    )


async def get_staff_dashboard(
    db: AsyncSession, current_user: user_model.User
) -> db_schema.StaffDashboardSummary:
    now = datetime.now(timezone.utc)
    today_date = now.date()

    today_appts = await appt_repository.list_appointments(
        db, date_str=today_date.strftime("%Y-%m-%d")
    )

    async def _count_status(status_str: str) -> int:
        q = select(func.count(appt_model.Appointment.id)).where(
            appt_model.Appointment.status == status_str
        )
        return (await db.execute(q)).scalar() or 0

    pending_c = await _count_status("pending")
    confirmed_c = await _count_status("confirmed")
    completed_c = await _count_status("completed")
    cancelled_c = await _count_status("cancelled")

    return db_schema.StaffDashboardSummary(
        today_count=len(today_appts),
        pending_count=pending_c,
        confirmed_count=confirmed_c,
        completed_count=completed_c,
        cancelled_count=cancelled_c,
        today_appointments=[
            appt_schema.AppointmentRead.model_validate(a) for a in today_appts
        ],
    )


async def get_admin_dashboard(
    db: AsyncSession, current_user: user_model.User
) -> db_schema.AdminDashboardSummary:
    now = datetime.now(timezone.utc)
    today_date = now.date()

    async def _count_users(role_str: str | None = None) -> int:
        q = select(func.count(user_model.User.id))
        if role_str:
            q = q.where(user_model.User.role == role_str)
        return (await db.execute(q)).scalar() or 0

    tot_users = await _count_users()
    tot_patients = await _count_users("patient")
    tot_doctors = await _count_users("doctor")
    tot_staff = await _count_users("staff")

    # Active doctors count
    q_act_docs = select(func.count(doctor_model.DoctorProfile.id)).where(
        doctor_model.DoctorProfile.is_active == True
    )
    act_docs = (await db.execute(q_act_docs)).scalar() or 0

    # Today's appointments count
    today_appts = await appt_repository.list_appointments(
        db, date_str=today_date.strftime("%Y-%m-%d")
    )

    async def _count_appt_status(status_str: str) -> int:
        q = select(func.count(appt_model.Appointment.id)).where(
            appt_model.Appointment.status == status_str
        )
        return (await db.execute(q)).scalar() or 0

    pend_c = await _count_appt_status("pending")
    conf_c = await _count_appt_status("confirmed")
    comp_c = await _count_appt_status("completed")
    canc_c = await _count_appt_status("cancelled")

    # Specialties count
    q_specs = select(func.count(specialty_model.Specialty.id))
    tot_specs = (await db.execute(q_specs)).scalar() or 0

    # Services count
    q_srvs = select(func.count(service_model.Service.id))
    tot_srvs = (await db.execute(q_srvs)).scalar() or 0

    return db_schema.AdminDashboardSummary(
        total_users=tot_users,
        total_patients=tot_patients,
        total_doctors=tot_doctors,
        total_staff=tot_staff,
        active_doctors_count=act_docs,
        today_appointments_count=len(today_appts),
        pending_count=pend_c,
        confirmed_count=conf_c,
        completed_count=comp_c,
        cancelled_count=canc_c,
        total_specialties=tot_specs,
        total_services=tot_srvs,
    )
