from sqlalchemy.orm import Session

from ..repository.UserRepository import UserRepository
from ..schemas.users import UserCreate, UserResponse

from ..dependencies.auth import get_password_hash

class UserService:
    def __init__ (self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def create_user(
        self,
        user_data: UserCreate,
    ) -> UserResponse:
        new_user = self.repository.create_user(
            email=user_data.email,
            full_name=user_data.full_name,
            phone_number=str(user_data.phone_number) if user_data.phone_number else None,
            password_hash=get_password_hash(user_data.password),
        )

        return UserResponse.model_validate(new_user)
        
        

