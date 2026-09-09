from sqlalchemy.orm import Session

from ..models.models import User
from ..schemas.users import CreateUser

class UserRepository:
    def __init__ (self, db: Session):
        self.db = db

    def create_user(self, user: CreateUser):
        return user.model_dump()


