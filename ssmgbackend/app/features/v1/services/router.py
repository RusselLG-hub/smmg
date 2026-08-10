from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.services import schema as service_schema
from app.features.v1.services import service as service_layer

router = APIRouter(prefix="/v1/services", tags=["services"])


@router.get("", response_model=list[service_schema.ServiceRead])
async def list_services(
    active_only: bool = Query(False),
    specialty_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await service_layer.list_services(
        db, active_only=active_only, specialty_id=specialty_id
    )


@router.get("/{service_id}", response_model=service_schema.ServiceRead)
async def get_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await service_layer.get_service(db, service_id)


@router.post(
    "",
    response_model=service_schema.ServiceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def create_service(
    data: service_schema.ServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service_layer.create_service(db, data)


@router.put(
    "/{service_id}",
    response_model=service_schema.ServiceRead,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def update_service(
    service_id: str,
    data: service_schema.ServiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await service_layer.update_service(db, service_id, data)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
):
    await service_layer.delete_service(db, service_id)
