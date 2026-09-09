from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.features.v1.patients import repository as patient_repository
from app.features.v1.patients import schema as patient_schema
from app.features.v1.patients.model import PatientProfile
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository
from app.features.v1.users import schema as user_schema


def _get_appointment_model():
    from app.features.v1.appointments.model import Appointment
    return Appointment


def _build_patient_record(
    profile: PatientProfile,
    appointments: list,
) -> patient_schema.PatientProfileRead:
    doctor_summary = None
    latest_status = None
    latest_ref = None
    all_statuses: list[str] = []

    if appointments:
        sorted_appts = sorted(
            appointments, key=lambda a: a.scheduled_at, reverse=True
        )
        active_appts = [a for a in sorted_appts if a.status in ("confirmed", "pending")]
        chosen_appt = active_appts[0] if active_appts else sorted_appts[0]

        if chosen_appt.doctor and chosen_appt.doctor.user:
            spec_name = (
                chosen_appt.doctor.specialty.name
                if chosen_appt.doctor.specialty
                else None
            )
            doctor_summary = patient_schema.PatientDoctorSummary(
                id=chosen_appt.doctor.id,
                name=chosen_appt.doctor.user.name,
                title=chosen_appt.doctor.title,
                specialty_name=spec_name,
            )
        latest_status = chosen_appt.status
        latest_ref = chosen_appt.appointment_reference
        all_statuses = list({a.status for a in appointments})

    return patient_schema.PatientProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        phone=profile.phone,
        address=profile.address,
        profile_image_url=profile.profile_image_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        user=user_schema.UserRead.model_validate(profile.user),
        doctor=doctor_summary,
        appointment_status=latest_status,
        appointment_reference=latest_ref,
        all_statuses=all_statuses,
    )


async def list_patient_records(
    db: AsyncSession,
) -> list[patient_schema.PatientProfileRead]:
    Appointment = _get_appointment_model()
    users = await user_repository.list_users(db, role="patient")
    appts_stmt = select(Appointment)
    appts_res = await db.execute(appts_stmt)
    all_appts = list(appts_res.scalars().all())

    appts_by_patient: dict[str, list] = {}
    for appt in all_appts:
        appts_by_patient.setdefault(appt.patient_profile_id, []).append(appt)

    records = []
    for user in users:
        profile = await patient_repository.get_or_create(db, user.id)
        records.append(_build_patient_record(profile, appts_by_patient.get(profile.id, [])))
    return records


async def get_patient_profile(
    db: AsyncSession, current_user: user_model.User
) -> patient_schema.PatientProfileRead:
    Appointment = _get_appointment_model()
    profile = await patient_repository.get_or_create(db, current_user.id)
    appts_stmt = select(Appointment).where(Appointment.patient_profile_id == profile.id)
    appts_res = await db.execute(appts_stmt)
    appts = list(appts_res.scalars().all())
    return _build_patient_record(profile, appts)


async def update_patient_profile(
    db: AsyncSession,
    current_user: user_model.User,
    data: patient_schema.PatientProfileUpdate,
) -> patient_schema.PatientProfileRead:
    if data.name:
        current_user.name = data.name.strip()
    if data.profile_image_url is not None:
        current_user.profile_image_url = data.profile_image_url
    if data.name or data.profile_image_url is not None:
        await db.commit()

    profile = await patient_repository.update(db, current_user.id, data)
    Appointment = _get_appointment_model()
    appts_stmt = select(Appointment).where(Appointment.patient_profile_id == profile.id)
    appts_res = await db.execute(appts_stmt)
    appts = list(appts_res.scalars().all())
    return _build_patient_record(profile, appts)


async def archive_patient(
    db: AsyncSession, patient_id: str
) -> patient_schema.PatientProfileRead:
    patient = await patient_repository.get_by_id(db, patient_id)
    if not patient:
        raise NotFoundException(detail="Patient profile not found")
    user = await user_repository.get_by_id(db, patient.user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    user.is_active = False
    await db.commit()
    await db.refresh(patient)
    Appointment = _get_appointment_model()
    appts_stmt = select(Appointment).where(Appointment.patient_profile_id == patient.id)
    appts_res = await db.execute(appts_stmt)
    appts = list(appts_res.scalars().all())
    return _build_patient_record(patient, appts)


async def restore_patient(
    db: AsyncSession, patient_id: str
) -> patient_schema.PatientProfileRead:
    patient = await patient_repository.get_by_id(db, patient_id)
    if not patient:
        raise NotFoundException(detail="Patient profile not found")
    user = await user_repository.get_by_id(db, patient.user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    user.is_active = True
    await db.commit()
    await db.refresh(patient)
    Appointment = _get_appointment_model()
    appts_stmt = select(Appointment).where(Appointment.patient_profile_id == patient.id)
    appts_res = await db.execute(appts_stmt)
    appts = list(appts_res.scalars().all())
    return _build_patient_record(patient, appts)


async def delete_patient(db: AsyncSession, patient_id: str) -> None:
    patient = await patient_repository.get_by_id(db, patient_id)
    if not patient:
        raise NotFoundException(detail="Patient profile not found")
    user_id = patient.user_id
    await patient_repository.delete(db, patient_id)
    user = await user_repository.get_by_id(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()


