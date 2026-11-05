import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.features.v1.users.schema import UserRead


class PatientDoctorSummary(BaseModel):
    id: str
    name: str
    title: str | None = None
    specialty_name: str | None = None


class PatientProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str | None = None
    address: str | None = None
    profile_image_url: str | None = None
    created_at: datetime
    updated_at: datetime
    user: UserRead
    doctor: PatientDoctorSummary | None = None
    appointment_status: str | None = None
    appointment_reference: str | None = None
    all_statuses: list[str] = []


class PatientProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    date_of_birth: str | None = Field(None, max_length=20)
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=255)
    profile_image_url: str | None = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_patient_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Full name cannot be empty.")
        parts = trimmed.split()
        if len(parts) < 2 or any(len(p) < 2 for p in parts) or not re.match(r"^[A-Za-zÀ-ÿ\s'.-]+$", trimmed):
            raise ValueError("Full name must include at least first and last name (letters only).")
        return trimmed

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        parsed_date = None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                parsed_date = datetime.strptime(trimmed, fmt).date()
                break
            except ValueError:
                continue
        if not parsed_date:
            raise ValueError("Date of birth must be a valid date.")
        current_date = datetime.now().date()
        if parsed_date.year < 1900 or parsed_date > current_date:
            raise ValueError("Date of birth must be between 1900 and today.")
        return parsed_date.strftime("%Y-%m-%d")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        cleaned = re.sub(r"[\s\-()]", "", trimmed)
        if not (re.match(r"^09\d{9}$", cleaned) or re.match(r"^\+639\d{9}$", cleaned) or re.match(r"^639\d{9}$", cleaned)):
            raise ValueError("Phone number must be a valid Philippine mobile number (e.g. 09123456789 or +639123456789).")
        if cleaned.startswith("09"):
            cleaned = "+63" + cleaned[1:]
        elif cleaned.startswith("639"):
            cleaned = "+" + cleaned
        return cleaned

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str | None) -> str | None:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        if len(trimmed) < 5 or not re.search(r"[A-Za-z]", trimmed):
            raise ValueError("Address must be at least 5 characters and include street/city details.")
        return trimmed
