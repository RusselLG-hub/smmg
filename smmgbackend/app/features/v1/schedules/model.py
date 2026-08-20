from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.features.v1.doctors.model import DoctorProfile
from app.helpers.ulid import generate_ulid


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    doctor_profile_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
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

    doctor_profile: Mapped[DoctorProfile] = relationship(
        "DoctorProfile", lazy="selectin"
    )


class DoctorScheduleOverride(Base):
    __tablename__ = "doctor_schedule_overrides"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    doctor_profile_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )  # YYYY-MM-DD
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    start_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # HH:MM
    end_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # HH:MM
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    doctor_profile: Mapped[DoctorProfile] = relationship(
        "DoctorProfile", lazy="selectin"
    )
