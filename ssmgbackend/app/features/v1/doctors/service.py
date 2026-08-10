from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.features.v1.doctors import repository as doctor_repository
from app.features.v1.doctors import schema as doctor_schema
from app.features.v1.specialties import repository as specialty_repository
from app.features.v1.users import repository as user_repository
from app.features.v1.users import schema as user_schema


async def list_doctors(
    db: AsyncSession, active_only: bool = False, specialty_id: str | None = None
) -> list[doctor_schema.DoctorRead]:
    items = await doctor_repository.get_all(
        db, active_only=active_only, specialty_id=specialty_id
    )
    return [doctor_schema.DoctorRead.model_validate(i) for i in items]


async def get_doctor(
    db: AsyncSession, doctor_id: str
) -> doctor_schema.DoctorRead:
    item = await doctor_repository.get_by_id(db, doctor_id)
    if not item:
        raise NotFoundException(detail="Doctor profile not found")
    return doctor_schema.DoctorRead.model_validate(item)


async def create_doctor(
    db: AsyncSession, data: doctor_schema.DoctorCreate
) -> doctor_schema.DoctorRead:
    existing_user = await user_repository.get_by_email(db, data.email)
    if existing_user:
        raise ConflictException(detail="Email is already registered")

    if data.specialty_id:
        spec = await specialty_repository.get_by_id(db, data.specialty_id)
        if not spec:
            raise NotFoundException(detail="Specialty not found")

    hashed_pw = hash_password(data.password)
    user_create = user_schema.UserCreate(
        email=data.email,
        name=data.name,
        password=data.password,
    )
    # Admin-created doctor accounts have role="doctor" and pre-verified email
    user = await user_repository.create_user(
        db, user_create=user_create, hashed_password=hashed_pw, role="doctor"
    )
    user.is_email_verified = True
    await db.commit()

    doctor = await doctor_repository.create(
        db,
        user_id=user.id,
        specialty_id=data.specialty_id,
        title=data.title,
        phone=data.phone,
        bio=data.bio,
        profile_image_url=data.profile_image_url,
        is_active=data.is_active,
    )

    doctor_full = await doctor_repository.get_by_id(db, doctor.id)
    return doctor_schema.DoctorRead.model_validate(doctor_full)


async def update_doctor(
    db: AsyncSession, doctor_id: str, data: doctor_schema.DoctorUpdate
) -> doctor_schema.DoctorRead:
    doctor = await doctor_repository.get_by_id(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor profile not found")

    if data.specialty_id:
        spec = await specialty_repository.get_by_id(db, data.specialty_id)
        if not spec:
            raise NotFoundException(detail="Specialty not found")

    if data.name:
        doctor.user.name = data.name.strip()
        await db.commit()

    updated = await doctor_repository.update(db, doctor_id, data)
    if not updated:
        raise NotFoundException(detail="Doctor profile not found")

    doctor_full = await doctor_repository.get_by_id(db, doctor_id)
    return doctor_schema.DoctorRead.model_validate(doctor_full)


async def delete_doctor(db: AsyncSession, doctor_id: str) -> None:
    doctor = await doctor_repository.get_by_id(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor profile not found")

    # Deleting doctor profile also handles user deletion if desired or cascade
    user_id = doctor.user_id
    await doctor_repository.delete(db, doctor_id)
    user = await user_repository.get_by_id(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
