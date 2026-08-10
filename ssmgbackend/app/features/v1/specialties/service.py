from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.features.v1.specialties import repository as specialty_repository
from app.features.v1.specialties import schema as specialty_schema


async def list_specialties(
    db: AsyncSession, active_only: bool = False
) -> list[specialty_schema.SpecialtyRead]:
    items = await specialty_repository.get_all(db, active_only=active_only)
    return [specialty_schema.SpecialtyRead.model_validate(i) for i in items]


async def get_specialty(
    db: AsyncSession, specialty_id: str
) -> specialty_schema.SpecialtyRead:
    item = await specialty_repository.get_by_id(db, specialty_id)
    if not item:
        raise NotFoundException(detail="Specialty not found")
    return specialty_schema.SpecialtyRead.model_validate(item)


async def create_specialty(
    db: AsyncSession, data: specialty_schema.SpecialtyCreate
) -> specialty_schema.SpecialtyRead:
    existing = await specialty_repository.get_by_name(db, data.name)
    if existing:
        raise ConflictException(detail="Specialty with this name already exists")

    item = await specialty_repository.create(db, data)
    return specialty_schema.SpecialtyRead.model_validate(item)


async def update_specialty(
    db: AsyncSession, specialty_id: str, data: specialty_schema.SpecialtyUpdate
) -> specialty_schema.SpecialtyRead:
    if data.name:
        existing = await specialty_repository.get_by_name(db, data.name)
        if existing and existing.id != specialty_id:
            raise ConflictException(detail="Specialty with this name already exists")

    item = await specialty_repository.update(db, specialty_id, data)
    if not item:
        raise NotFoundException(detail="Specialty not found")
    return specialty_schema.SpecialtyRead.model_validate(item)


async def delete_specialty(db: AsyncSession, specialty_id: str) -> None:
    deleted = await specialty_repository.delete(db, specialty_id)
    if not deleted:
        raise NotFoundException(detail="Specialty not found")
