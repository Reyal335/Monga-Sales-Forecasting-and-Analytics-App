from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None =  None

class CreateUser(User):
    phone_number: PhoneNumber

class UserInDB(User):
    hashed_password: str