# app/schemas/users.py
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=8)
    phone_number: PhoneNumber | None = None
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: EmailStr
    full_name: str
    phone_number: str | None
    is_active: bool
    is_email_verified: bool


class UserInDB(UserResponse):
    password_hash: str