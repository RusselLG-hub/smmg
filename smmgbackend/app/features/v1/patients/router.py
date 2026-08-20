from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import require_role
from app.features.v1.patients import schema as patient_schema
from app.features.v1.patients import service as patient_service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/patients", tags=["patients"])


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
