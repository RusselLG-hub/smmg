from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.doctors.model import DoctorProfile
from app.features.v1.doctors.schema import DoctorUpdate


async def get_all(
    db: AsyncSession, active_only: bool = False, specialty_id: str | None = None
) -> list[DoctorProfile]:
    stmt = select(DoctorProfile)
    if active_only:
        stmt = stmt.where(DoctorProfile.is_active == True)
    if specialty_id:
        stmt = stmt.where(DoctorProfile.specialty_id == specialty_id)
    stmt = stmt.order_by(DoctorProfile.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, doctor_id: str) -> DoctorProfile | None:
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.id == doctor_id)
    )
    return result.scalar_one_or_none()


async def get_by_user_id(db: AsyncSession, user_id: str) -> DoctorProfile | None:
    result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: str,
    specialty_id: str | None = None,
    title: str | None = None,
    phone: str | None = None,
    bio: str | None = None,
    profile_image_url: str | None = None,
    is_active: bool = True,
) -> DoctorProfile:
    doctor = DoctorProfile(
        user_id=user_id,
        specialty_id=specialty_id,
        title=title,
        phone=phone,
        bio=bio,
        profile_image_url=profile_image_url,
        is_active=is_active,
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


async def get_or_create(db: AsyncSession, user_id: str) -> DoctorProfile:
    doctor = await get_by_user_id(db, user_id)
    if doctor:
        return doctor
    try:
        return await create(db, user_id=user_id)
    except IntegrityError:
        # The layout and profile page can request /me at the same time. The
        # unique user_id constraint lets one create win; load that row here.
        await db.rollback()
        doctor = await get_by_user_id(db, user_id)
        if doctor:
            return doctor
        raise


async def update(
    db: AsyncSession, doctor_id: str, data: DoctorUpdate
) -> DoctorProfile | None:
    doctor = await get_by_id(db, doctor_id)
    if not doctor:
        return None

    if data.specialty_id is not None:
        doctor.specialty_id = data.specialty_id
    if data.title is not None:
        doctor.title = data.title.strip() if data.title else None
    if data.phone is not None:
        doctor.phone = data.phone.strip() if data.phone else None
    if data.bio is not None:
        doctor.bio = data.bio.strip() if data.bio else None
    if data.profile_image_url is not None:
        doctor.profile_image_url = data.profile_image_url
    if data.is_active is not None:
        doctor.is_active = data.is_active

    await db.commit()
    await db.refresh(doctor)
    return doctor


async def delete(db: AsyncSession, doctor_id: str) -> bool:
    doctor = await get_by_id(db, doctor_id)
    if not doctor:
        return False
    await db.delete(doctor)
    await db.commit()
    return True
