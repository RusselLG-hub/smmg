from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.auth.dependencies import get_current_user, require_role
from app.features.v1.reports import schema as reports_schema
from app.features.v1.reports import service as reports_service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get(
    "/overview",
    response_model=reports_schema.ReportsOverviewResponse,
    dependencies=[Depends(require_role("staff", "admin"))],
)
async def get_reports_overview(
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    return await reports_service.get_reports_overview(
        db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/doctor/me",
    response_model=reports_schema.DoctorPersonalReportResponse,
    dependencies=[Depends(require_role("doctor"))],
)
async def get_doctor_personal_report(
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    return await reports_service.get_doctor_personal_report(
        db, current_user, start_date=start_date, end_date=end_date
    )
