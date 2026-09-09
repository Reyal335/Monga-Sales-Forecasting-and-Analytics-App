from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    username: str = Field(min_length=8)
    email: str | None = None
    full_name: str = Field(min_length=8)
    is_active: bool | None =  None

class CreateUser(User):
    phone_number: PhoneNumber
    password: str = Field(min_length=8)

class UserInDB(User):
    hashed_password: str