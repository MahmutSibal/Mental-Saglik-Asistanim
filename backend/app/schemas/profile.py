from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)


class AvatarUploadResponse(BaseModel):
    avatar_url: str
