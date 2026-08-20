from datetime import date, datetime, timezone
from sqlalchemy import case, cast, Date, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.appointments.model import Appointment
from app.features.v1.doctors.model import DoctorProfile
from app.features.v1.patients.model import PatientProfile
from app.features.v1.services.model import Service
from app.features.v1.specialties.model import Specialty
from app.features.v1.users.model import User


async def get_status_counts(
    db: AsyncSession, start_dt: datetime, end_dt: datetime, doctor_id: str | None = None
) -> dict[str, int]:
    stmt = select(
        Appointment.status,
        func.count(Appointment.id).label("cnt"),
    ).where(
        Appointment.scheduled_at >= start_dt,
        Appointment.scheduled_at <= end_dt,
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)

    stmt = stmt.group_by(Appointment.status)
    result = await db.execute(stmt)

    counts = {"pending": 0, "confirmed": 0, "completed": 0, "cancelled": 0}
    for row in result.all():
        if row.status in counts:
            counts[row.status] = row.cnt

    return counts


async def get_volume_trend(
    db: AsyncSession, start_dt: datetime, end_dt: datetime, doctor_id: str | None = None
) -> list[tuple[date, int]]:
    date_col = cast(Appointment.scheduled_at, Date)
    stmt = (
        select(date_col.label("appt_date"), func.count(Appointment.id).label("cnt"))
        .where(
            Appointment.scheduled_at >= start_dt,
            Appointment.scheduled_at <= end_dt,
        )
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)

    stmt = stmt.group_by(date_col).order_by(date_col)
    result = await db.execute(stmt)
    return [(row.appt_date, row.cnt) for row in result.all()]


async def get_doctor_stats(
    db: AsyncSession, start_dt: datetime, end_dt: datetime
) -> list[dict]:
    stmt = (
        select(
            DoctorProfile.id.label("doctor_id"),
            User.name.label("doctor_name"),
            Specialty.name.label("specialty_name"),
            func.count(Appointment.id).label("total_cnt"),
            func.count(case((Appointment.status == "completed", 1))).label("completed_cnt"),
            func.count(case((Appointment.status == "cancelled", 1))).label("cancelled_cnt"),
            func.count(case((Appointment.status == "pending", 1))).label("pending_cnt"),
            func.count(case((Appointment.status == "confirmed", 1))).label("confirmed_cnt"),
        )
        .join(User, DoctorProfile.user_id == User.id)
        .outerjoin(Specialty, DoctorProfile.specialty_id == Specialty.id)
        .outerjoin(
            Appointment,
            (Appointment.doctor_profile_id == DoctorProfile.id)
            & (Appointment.scheduled_at >= start_dt)
            & (Appointment.scheduled_at <= end_dt),
        )
        .group_by(DoctorProfile.id, User.name, Specialty.name)
        .order_by(func.count(Appointment.id).desc())
    )

    result = await db.execute(stmt)
    rows = []
    for row in result.all():
        rows.append(
            {
                "doctor_profile_id": row.doctor_id,
                "doctor_name": row.doctor_name,
                "specialty_name": row.specialty_name,
                "total_appointments": row.total_cnt,
                "completed_appointments": row.completed_cnt,
                "cancelled_appointments": row.cancelled_cnt,
                "pending_appointments": row.pending_cnt,
                "confirmed_appointments": row.confirmed_cnt,
            }
        )
    return rows


async def get_service_stats(
    db: AsyncSession, start_dt: datetime, end_dt: datetime, doctor_id: str | None = None
) -> tuple[list[dict], int]:
    stmt = (
        select(
            Service.id.label("service_id"),
            Service.name.label("service_name"),
            Specialty.name.label("specialty_name"),
            func.count(Appointment.id).label("total_cnt"),
            func.count(case((Appointment.status == "completed", 1))).label("completed_cnt"),
            func.count(case((Appointment.status == "cancelled", 1))).label("cancelled_cnt"),
        )
        .outerjoin(Specialty, Service.specialty_id == Specialty.id)
        .join(Appointment, Appointment.service_id == Service.id)
        .where(
            Appointment.scheduled_at >= start_dt,
            Appointment.scheduled_at <= end_dt,
        )
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)

    stmt = stmt.group_by(Service.id, Service.name, Specialty.name).order_by(
        func.count(Appointment.id).desc()
    )

    result = await db.execute(stmt)
    rows = []
    grand_total = 0
    for row in result.all():
        grand_total += row.total_cnt
        rows.append(
            {
                "service_id": row.service_id,
                "service_name": row.service_name,
                "specialty_name": row.specialty_name,
                "appointment_count": row.total_cnt,
                "completed_count": row.completed_cnt,
                "cancelled_count": row.cancelled_cnt,
            }
        )

    return rows, grand_total


async def get_specialty_stats(
    db: AsyncSession, start_dt: datetime, end_dt: datetime
) -> list[dict]:
    # Doctors per specialty
    doc_stmt = select(
        Specialty.id,
        func.count(DoctorProfile.id).label("doc_cnt"),
    ).outerjoin(DoctorProfile, DoctorProfile.specialty_id == Specialty.id).group_by(Specialty.id)
    doc_res = dict((r.id, r.doc_cnt) for r in (await db.execute(doc_stmt)).all())

    # Services per specialty
    srv_stmt = select(
        Specialty.id,
        func.count(Service.id).label("srv_cnt"),
    ).outerjoin(Service, Service.specialty_id == Specialty.id).group_by(Specialty.id)
    srv_res = dict((r.id, r.srv_cnt) for r in (await db.execute(srv_stmt)).all())

    # Appointments per specialty
    appt_stmt = (
        select(
            Specialty.id.label("spec_id"),
            Specialty.name.label("spec_name"),
            func.count(Appointment.id).label("appt_cnt"),
        )
        .outerjoin(DoctorProfile, DoctorProfile.specialty_id == Specialty.id)
        .outerjoin(
            Appointment,
            (Appointment.doctor_profile_id == DoctorProfile.id)
            & (Appointment.scheduled_at >= start_dt)
            & (Appointment.scheduled_at <= end_dt),
        )
        .group_by(Specialty.id, Specialty.name)
        .order_by(func.count(Appointment.id).desc())
    )

    result = await db.execute(appt_stmt)
    rows = []
    for r in result.all():
        rows.append(
            {
                "specialty_id": r.spec_id,
                "specialty_name": r.spec_name,
                "doctor_count": doc_res.get(r.spec_id, 0),
                "appointment_count": r.appt_cnt,
                "service_count": srv_res.get(r.spec_id, 0),
            }
        )
    return rows


async def get_peak_days(
    db: AsyncSession, start_dt: datetime, end_dt: datetime, doctor_id: str | None = None
) -> list[tuple[int, int]]:
    dow_col = extract("dow", Appointment.scheduled_at)
    stmt = select(dow_col.label("dow"), func.count(Appointment.id).label("cnt")).where(
        Appointment.scheduled_at >= start_dt,
        Appointment.scheduled_at <= end_dt,
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)

    stmt = stmt.group_by(dow_col).order_by(dow_col)
    res = await db.execute(stmt)
    return [(int(r.dow), r.cnt) for r in res.all()]


async def get_peak_hours(
    db: AsyncSession, start_dt: datetime, end_dt: datetime, doctor_id: str | None = None
) -> list[tuple[int, int]]:
    hour_col = extract("hour", Appointment.scheduled_at)
    stmt = select(hour_col.label("hr"), func.count(Appointment.id).label("cnt")).where(
        Appointment.scheduled_at >= start_dt,
        Appointment.scheduled_at <= end_dt,
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_profile_id == doctor_id)

    stmt = stmt.group_by(hour_col).order_by(hour_col)
    res = await db.execute(stmt)
    return [(int(r.hr), r.cnt) for r in res.all()]


async def get_demographic_stats(db: AsyncSession) -> dict:
    # Gender distribution
    gender_stmt = select(
        PatientProfile.gender,
        func.count(PatientProfile.id).label("cnt"),
    ).group_by(PatientProfile.gender)
    gender_res = (await db.execute(gender_stmt)).all()

    genders = {"Male": 0, "Female": 0, "Other": 0, "Unspecified": 0}
    tot_patients = 0
    for r in gender_res:
        tot_patients += r.cnt
        g_key = (r.gender or "").capitalize()
        if g_key in genders:
            genders[g_key] += r.cnt
        else:
            genders["Unspecified"] += r.cnt

    # Age distribution using date_of_birth
    now_date = date.today()

    all_dobs_stmt = select(PatientProfile.date_of_birth).where(
        PatientProfile.date_of_birth.isnot(None)
    )
    dobs = (await db.execute(all_dobs_stmt)).scalars().all()

    age_groups = {
        "Under 18": 0,
        "18-35": 0,
        "36-50": 0,
        "51-65": 0,
        "65+": 0,
        "Unspecified": tot_patients - len(dobs),
    }

    for dob_str in dobs:
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            age = (
                now_date.year
                - dob.year
                - ((now_date.month, now_date.day) < (dob.month, dob.day))
            )
            if age < 18:
                age_groups["Under 18"] += 1
            elif age <= 35:
                age_groups["18-35"] += 1
            elif age <= 50:
                age_groups["36-50"] += 1
            elif age <= 65:
                age_groups["51-65"] += 1
            else:
                age_groups["65+"] += 1
        except Exception:
            age_groups["Unspecified"] += 1

    return {
        "total_patients": tot_patients,
        "gender_distribution": [
            {"label": k, "count": v} for k, v in genders.items()
        ],
        "age_distribution": [
            {"label": k, "count": v} for k, v in age_groups.items()
        ],
    }
