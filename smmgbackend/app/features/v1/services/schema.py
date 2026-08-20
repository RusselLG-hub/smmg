from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.features.v1.specialties.schema import SpecialtyRead


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    specialty_id: str | None = None
    image_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    specialty: SpecialtyRead | None = None


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    specialty_id: str | None = None
    image_url: str | None = Field(None, max_length=500)
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, max_length=1000)
    specialty_id: str | None = None
    image_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None
