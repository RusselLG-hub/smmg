from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.features.v1.specialties.schema import SpecialtyRead
from app.features.v1.users.schema import UserRead


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    specialty_id: str | None = None
    title: str | None = None
    phone: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user: UserRead
    specialty: SpecialtyRead | None = None


class DoctorCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    specialty_id: str | None = None
    title: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    bio: str | None = Field(None, max_length=1000)
    profile_image_url: str | None = Field(None, max_length=500)
    is_active: bool = True


class DoctorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    specialty_id: str | None = None
    title: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    bio: str | None = Field(None, max_length=1000)
    profile_image_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None
