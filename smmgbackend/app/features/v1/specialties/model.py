from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.helpers.ulid import generate_ulid


class Specialty(Base):
    __tablename__ = "specialties"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
