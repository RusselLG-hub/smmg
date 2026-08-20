from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.specialties.model import Specialty
from app.features.v1.specialties.schema import SpecialtyCreate, SpecialtyUpdate


async def get_all(
    db: AsyncSession, active_only: bool = False
) -> list[Specialty]:
    stmt = select(Specialty)
    if active_only:
        stmt = stmt.where(Specialty.is_active == True)
    stmt = stmt.order_by(Specialty.name.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, specialty_id: str) -> Specialty | None:
    result = await db.execute(
        select(Specialty).where(Specialty.id == specialty_id)
    )
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Specialty | None:
    result = await db.execute(
        select(Specialty).where(Specialty.name.ilike(name.strip()))
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: SpecialtyCreate) -> Specialty:
    specialty = Specialty(
        name=data.name.strip(),
        description=data.description.strip() if data.description else None,
        is_active=data.is_active,
    )
    db.add(specialty)
    await db.commit()
    await db.refresh(specialty)
    return specialty


async def update(
    db: AsyncSession, specialty_id: str, data: SpecialtyUpdate
) -> Specialty | None:
    specialty = await get_by_id(db, specialty_id)
    if not specialty:
        return None

    if data.name is not None:
        specialty.name = data.name.strip()
    if data.description is not None:
        specialty.description = data.description.strip() if data.description else None
    if data.is_active is not None:
        specialty.is_active = data.is_active

    await db.commit()
    await db.refresh(specialty)
    return specialty


async def delete(db: AsyncSession, specialty_id: str) -> bool:
    specialty = await get_by_id(db, specialty_id)
    if not specialty:
        return False
    await db.delete(specialty)
    await db.commit()
    return True
