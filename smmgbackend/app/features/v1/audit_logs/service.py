from math import ceil
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.audit_logs import repository as audit_repo
from app.features.v1.audit_logs.schema import (
    AuditLogListResponse,
    AuditLogRead,
    AuditStats,
    PaginationMeta,
)


async def log_event(
    db: AsyncSession,
    *,
    action: str,
    description: str,
    user_id: str | None = None,
    user_name: str | None = None,
    user_role: str | None = None,
    auditable_type: str | None = None,
    auditable_id: str | None = None,
    properties: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLogRead:
    log = await audit_repo.create_log(
        db,
        action=action,
        description=description,
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        auditable_type=auditable_type,
        auditable_id=auditable_id,
        properties=properties,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return AuditLogRead.model_validate(log)


async def get_audit_logs(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 20,
    action: str | None = None,
    role: str | None = None,
    search: str | None = None,
) -> AuditLogListResponse:
    safe_page = max(1, page)
    safe_per_page = min(100, max(5, per_page))

    logs, total, today_count, actions_count = await audit_repo.list_logs(
        db,
        page=safe_page,
        per_page=safe_per_page,
        action=action,
        role=role,
        search=search,
    )

    last_page = max(1, ceil(total / safe_per_page))

    return AuditLogListResponse(
        logs=[AuditLogRead.model_validate(log) for log in logs],
        pagination=PaginationMeta(
            current_page=safe_page,
            last_page=last_page,
            per_page=safe_per_page,
            total=total,
        ),
        stats=AuditStats(
            total_logs=total,
            today_logs=today_count,
            actions_count=actions_count,
        ),
    )
