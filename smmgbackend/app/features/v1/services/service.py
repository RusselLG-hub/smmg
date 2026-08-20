from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.features.v1.services import repository as service_repository
from app.features.v1.services import schema as service_schema
from app.features.v1.specialties import repository as specialty_repository


async def list_services(
    db: AsyncSession, active_only: bool = False, specialty_id: str | None = None
) -> list[service_schema.ServiceRead]:
    items = await service_repository.get_all(
        db, active_only=active_only, specialty_id=specialty_id
    )
    return [service_schema.ServiceRead.model_validate(i) for i in items]


async def get_service(
    db: AsyncSession, service_id: str
) -> service_schema.ServiceRead:
    item = await service_repository.get_by_id(db, service_id)
    if not item:
        raise NotFoundException(detail="Service not found")
    return service_schema.ServiceRead.model_validate(item)


async def create_service(
    db: AsyncSession, data: service_schema.ServiceCreate
) -> service_schema.ServiceRead:
    existing = await service_repository.get_by_name(db, data.name)
    if existing:
        raise ConflictException(detail="Service with this name already exists")

    if data.specialty_id:
        spec = await specialty_repository.get_by_id(db, data.specialty_id)
        if not spec:
            raise NotFoundException(detail="Specialty not found")

    item = await service_repository.create(db, data)
    return service_schema.ServiceRead.model_validate(item)


async def update_service(
    db: AsyncSession, service_id: str, data: service_schema.ServiceUpdate
) -> service_schema.ServiceRead:
    if data.name:
        existing = await service_repository.get_by_name(db, data.name)
        if existing and existing.id != service_id:
            raise ConflictException(detail="Service with this name already exists")

    if data.specialty_id:
        spec = await specialty_repository.get_by_id(db, data.specialty_id)
        if not spec:
            raise NotFoundException(detail="Specialty not found")

    item = await service_repository.update(db, service_id, data)
    if not item:
        raise NotFoundException(detail="Service not found")
    return service_schema.ServiceRead.model_validate(item)


async def delete_service(db: AsyncSession, service_id: str) -> None:
    deleted = await service_repository.delete(db, service_id)
    if not deleted:
        raise NotFoundException(detail="Service not found")
