from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.patients import repository as patient_repository
from app.features.v1.patients import schema as patient_schema
from app.features.v1.users import model as user_model
from app.features.v1.users import repository as user_repository


async def list_patient_records(
    db: AsyncSession,
) -> list[patient_schema.PatientProfileRead]:
    users = await user_repository.list_users(db, role="patient")
    records = []
    for user in users:
        profile = await patient_repository.get_or_create(db, user.id)
        records.append(patient_schema.PatientProfileRead.model_validate(profile))
    return records


async def get_patient_profile(
    db: AsyncSession, current_user: user_model.User
) -> patient_schema.PatientProfileRead:
    profile = await patient_repository.get_or_create(db, current_user.id)
    return patient_schema.PatientProfileRead.model_validate(profile)


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
    return patient_schema.PatientProfileRead.model_validate(profile)

