from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.features.v1.users.schema import UserRead


class AIChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime


class AIChatMessageCreate(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User health query or message content",
    )


class AIChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class AIChatSessionCreate(BaseModel):
    title: str | None = Field(None, max_length=255)


class AIChatSessionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str | None = None
    messages: list[AIChatMessageRead] = []
    created_at: datetime
    updated_at: datetime


class AIChatAdminSessionRead(AIChatSessionRead):
    user: UserRead
    message_count: int = 0


class AIChatAdminSessionDetail(AIChatSessionDetail):
    user: UserRead
