from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.features.v1.doctors.model import DoctorProfile
from app.features.v1.patients.model import PatientProfile
from app.features.v1.services.model import Service
from app.helpers.ulid import generate_ulid


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    appointment_reference: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )
    patient_profile_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_profile_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("clinic_services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="confirmed", nullable=False, index=True
    )  # pending, confirmed, cancelled, completed
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
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

    patient: Mapped[PatientProfile] = relationship("PatientProfile", lazy="selectin")
    doctor: Mapped[DoctorProfile] = relationship("DoctorProfile", lazy="selectin")
    service: Mapped[Service | None] = relationship("Service", lazy="selectin")

    __table_args__ = (
        Index(
            "uq_active_doctor_scheduled_slot",
            "doctor_profile_id",
            "scheduled_at",
            unique=True,
            postgresql_where=text("status IN ('pending', 'confirmed')"),
        ),
    )
