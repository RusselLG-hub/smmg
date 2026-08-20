from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SpecialtyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SpecialtyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool = True


class SpecialtyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None
