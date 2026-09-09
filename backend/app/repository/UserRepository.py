from sqlalchemy.orm import Session

from ..models.models import User

class UserRepository:
    def __init__ (self, db: Session):
        self.db = db

    # def create_user(user: CreateUser):
    #     new_user = CreateUser(user)

