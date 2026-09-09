from typing import List, Dict, Any

from sqlalchemy.orm import Session

from ..repository.UserRepository import UserRepository
from ..schemas.users import CreateUser

class UserService:
    def __init__ (self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def create_user(
        self,
        user: CreateUser
    ) -> Dict[str, Any]:
        result = self.respository.create_user(user)


        # return created
        
        

