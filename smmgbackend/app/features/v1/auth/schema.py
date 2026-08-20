from pydantic import BaseModel, EmailStr, Field
from app.features.v1.users.schema import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    profile_image_url: str | None = Field(None, max_length=500)


class PasswordChangeConfirmRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseModel):
    user: UserRead
    message: str


class MessageResponse(BaseModel):
    message: str
