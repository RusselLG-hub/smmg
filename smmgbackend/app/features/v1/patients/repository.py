from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.patients.model import PatientProfile
from app.features.v1.patients.schema import PatientProfileUpdate


async def get_by_user_id(db: AsyncSession, user_id: str) -> PatientProfile | None:
    result = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_or_create(db: AsyncSession, user_id: str) -> PatientProfile:
    patient = await get_by_user_id(db, user_id)
    if not patient:
        patient = PatientProfile(user_id=user_id)
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
    return patient


async def update(
    db: AsyncSession, user_id: str, data: PatientProfileUpdate
) -> PatientProfile:
    patient = await get_or_create(db, user_id)

    if data.date_of_birth is not None:
        patient.date_of_birth = data.date_of_birth.strip() if data.date_of_birth else None
    if data.gender is not None:
        patient.gender = data.gender.strip() if data.gender else None
    if data.phone is not None:
        patient.phone = data.phone.strip() if data.phone else None
    if data.address is not None:
        patient.address = data.address.strip() if data.address else None
    if data.profile_image_url is not None:
        patient.profile_image_url = data.profile_image_url

    await db.commit()
    await db.refresh(patient)
    return patient
