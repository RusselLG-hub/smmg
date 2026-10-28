from datetime import datetime, timezone
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.v1.audit_logs.model import AuditLog


async def create_log(
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
) -> AuditLog:
    log = AuditLog(
        action=action.upper(),
        description=description,
        user_id=user_id,
        user_name=user_name,
        user_role=user_role.capitalize() if user_role else "System",
        auditable_type=auditable_type,
        auditable_id=auditable_id,
        properties=properties,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    await db.flush()
    return log


async def list_logs(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 20,
    action: str | None = None,
    role: str | None = None,
    search: str | None = None,
) -> tuple[list[AuditLog], int, int, dict[str, int]]:
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    if action:
        query = query.where(AuditLog.action == action.upper())
        count_query = count_query.where(AuditLog.action == action.upper())

    if role:
        query = query.where(func.lower(AuditLog.user_role) == role.lower())
        count_query = count_query.where(func.lower(AuditLog.user_role) == role.lower())

    if search:
        search_pattern = f"%{search}%"
        search_cond = (
            AuditLog.description.ilike(search_pattern)
            | AuditLog.user_name.ilike(search_pattern)
            | AuditLog.action.ilike(search_pattern)
            | AuditLog.ip_address.ilike(search_pattern)
        )
        query = query.where(search_cond)
        count_query = count_query.where(search_cond)

    # Total count for filtered query
    total_res = await db.scalar(count_query)
    total = total_res or 0

    # Paginate
    offset = (page - 1) * per_page
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page)
    result = await db.scalars(query)
    logs = list(result.all())

    # Today's logs
    now_utc = datetime.now(timezone.utc)
    today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today_start)
    ) or 0

    # Action counts (top 8)
    action_counts_query = (
        select(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
        .limit(8)
    )
    action_counts_res = await db.execute(action_counts_query)
    actions_count = {row[0]: row[1] for row in action_counts_res.all()}

    return logs, total, today_count, actions_count
