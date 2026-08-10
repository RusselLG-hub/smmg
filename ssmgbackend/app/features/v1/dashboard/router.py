from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import get_current_user, require_role
from app.features.v1.dashboard import schema as dashboard_schema
from app.features.v1.dashboard import service as dashboard_service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get(
    "/patient",
    response_model=dashboard_schema.PatientDashboardSummary,
    dependencies=[Depends(require_role("patient"))],
)
async def get_patient_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await dashboard_service.get_patient_dashboard(db, current_user)


@router.get(
    "/doctor",
    response_model=dashboard_schema.DoctorDashboardSummary,
    dependencies=[Depends(require_role("doctor"))],
)
async def get_doctor_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await dashboard_service.get_doctor_dashboard(db, current_user)


@router.get(
    "/staff",
    response_model=dashboard_schema.StaffDashboardSummary,
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def get_staff_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await dashboard_service.get_staff_dashboard(db, current_user)


@router.get(
    "/admin",
    response_model=dashboard_schema.AdminDashboardSummary,
    dependencies=[Depends(require_role("admin"))],
)
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await dashboard_service.get_admin_dashboard(db, current_user)
