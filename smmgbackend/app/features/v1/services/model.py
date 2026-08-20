from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.features.v1.specialties.model import Specialty
from app.helpers.ulid import generate_ulid


class Service(Base):
    __tablename__ = "clinic_services"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    name: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    specialty_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("specialties.id", ondelete="SET NULL"), nullable=True, index=True
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
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

    specialty: Mapped[Specialty | None] = relationship("Specialty", lazy="selectin")
