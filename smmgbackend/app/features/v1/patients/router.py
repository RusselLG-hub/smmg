from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.patients import schema as patient_schema
from app.features.v1.patients import service as patient_service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/patients", tags=["patients"])


@router.get(
    "",
    response_model=list[patient_schema.PatientProfileRead],
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def list_patient_records(db: AsyncSession = Depends(get_db)):
    return await patient_service.list_patient_records(db)


@router.get("/me", response_model=patient_schema.PatientProfileRead)
async def get_my_profile(
    current_user: user_model.User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    return await patient_service.get_patient_profile(db, current_user)


@router.put("/me", response_model=patient_schema.PatientProfileRead)
async def update_my_profile(
    data: patient_schema.PatientProfileUpdate,
    current_user: user_model.User = Depends(require_role("patient")),
    db: AsyncSession = Depends(get_db),
):
    return await patient_service.update_patient_profile(db, current_user, data)


@router.patch(
    "/{patient_id}/archive",
    response_model=patient_schema.PatientProfileRead,
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def archive_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await patient_service.archive_patient(db, patient_id)


@router.patch(
    "/{patient_id}/restore",
    response_model=patient_schema.PatientProfileRead,
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def restore_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await patient_service.restore_patient(db, patient_id)


@router.delete(
    "/{patient_id}",
    status_code=204,
    dependencies=[Depends(require_role("admin", "staff"))],
)
async def delete_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    await patient_service.delete_patient(db, patient_id)

