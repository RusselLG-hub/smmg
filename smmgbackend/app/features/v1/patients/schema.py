from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.features.v1.users.schema import UserRead


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


class PatientProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    date_of_birth: str | None = Field(None, max_length=20)
    gender: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=255)
    profile_image_url: str | None = Field(None, max_length=500)
