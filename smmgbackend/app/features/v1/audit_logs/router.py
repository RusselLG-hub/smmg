from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.v1.audit_logs import service as audit_service
from app.features.v1.audit_logs.schema import AuditLogListResponse
from app.features.v1.auth.dependencies import require_role

router = APIRouter(prefix="/v1/audit-logs", tags=["audit-logs"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=5, le=100, description="Items per page"),
    action: str | None = Query(None, description="Filter by action"),
    role: str | None = Query(None, description="Filter by user role"),
    search: str | None = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_db),
):
    return await audit_service.get_audit_logs(
        db,
        page=page,
        per_page=per_page,
        action=action,
        role=role,
        search=search,
    )
