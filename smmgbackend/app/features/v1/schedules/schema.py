from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DoctorScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doctor_profile_id: str
    day_of_week: int
    start_time: str
    end_time: str
    slot_duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DoctorScheduleCreate(BaseModel):
    doctor_profile_id: str | None = None
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", description="HH:MM format")
    end_time: str = Field(..., pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", description="HH:MM format")
    slot_duration_minutes: int = Field(30, gt=0, le=240)
    is_active: bool = True


class DoctorScheduleUpdate(BaseModel):
    day_of_week: int | None = Field(None, ge=0, le=6)
    start_time: str | None = Field(None, pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str | None = Field(None, pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    slot_duration_minutes: int | None = Field(None, gt=0, le=240)
    is_active: bool | None = None


class DoctorScheduleOverrideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doctor_profile_id: str
    date: str
    is_available: bool
    start_time: str | None = None
    end_time: str | None = None
    reason: str | None = None
    created_at: datetime


class DoctorScheduleOverrideCreate(BaseModel):
    doctor_profile_id: str | None = None
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    is_available: bool = False
    start_time: str | None = Field(None, pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str | None = Field(None, pattern=r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    reason: str | None = Field(None, max_length=255)


class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    is_available: bool = True


class AvailabilityResponse(BaseModel):
    doctor_id: str
    date: str
    day_of_week: int
    is_working_day: bool
    slots: list[TimeSlot]
