from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.services.model import Service
from app.features.v1.services.schema import ServiceCreate, ServiceUpdate


async def get_all(
    db: AsyncSession, active_only: bool = False, specialty_id: str | None = None
) -> list[Service]:
    stmt = select(Service)
    if active_only:
        stmt = stmt.where(Service.is_active == True)
    if specialty_id:
        stmt = stmt.where(Service.specialty_id == specialty_id)
    stmt = stmt.order_by(Service.name.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, service_id: str) -> Service | None:
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Service | None:
    result = await db.execute(
        select(Service).where(Service.name.ilike(name.strip()))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: ServiceCreate) -> Service:
    service = Service(
        name=data.name.strip(),
        description=data.description.strip() if data.description else None,
        specialty_id=data.specialty_id,
        image_url=data.image_url,
        is_active=data.is_active,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def update(
    db: AsyncSession, service_id: str, data: ServiceUpdate
) -> Service | None:
    service = await get_by_id(db, service_id)
    if not service:
        return None

    if data.name is not None:
        service.name = data.name.strip()
    if data.description is not None:
        service.description = data.description.strip() if data.description else None
    if data.specialty_id is not None:
        service.specialty_id = data.specialty_id
    if data.image_url is not None:
        service.image_url = data.image_url
    if data.is_active is not None:
        service.is_active = data.is_active

    await db.commit()
    await db.refresh(service)
    return service


async def delete(db: AsyncSession, service_id: str) -> bool:
    service = await get_by_id(db, service_id)
    if not service:
        return False
    await db.delete(service)
    await db.commit()
    return True
