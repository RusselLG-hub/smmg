import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.features.v1.doctors.schema import DoctorRead
from app.features.v1.patients.schema import PatientProfileRead
from app.features.v1.services.schema import ServiceRead


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    appointment_reference: str
    patient_profile_id: str
    doctor_profile_id: str
    service_id: str | None = None
    scheduled_at: datetime
    slot_duration_minutes: int
    status: str
    reason: str | None = None
    cancellation_reason: str | None = None
    reminder_sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    patient: PatientProfileRead
    doctor: DoctorRead
    service: ServiceRead | None = None


class AppointmentCreate(BaseModel):
    doctor_profile_id: str
    service_id: str | None = None
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    time: str = Field(..., pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", description="HH:MM")
    reason: str | None = Field(None, max_length=500)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        if len(re.findall(r"[A-Za-z]{2,}", trimmed)) < 1:
            raise ValueError("Chief complaint / reason for visit must include descriptive words describing your medical concern.")
        return trimmed


class AppointmentReschedule(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    time: str = Field(..., pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", description="HH:MM")


class AppointmentCancel(BaseModel):
    cancellation_reason: str | None = Field(None, max_length=255)


class AppointmentStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(pending|confirmed|cancelled|completed)$")
