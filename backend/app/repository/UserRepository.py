from sqlalchemy.orm import Session

from ..models.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        *,
        email: str,
        full_name: str,
        phone_number: str | None,
        password_hash: str,
    ) -> User:
        new_user = User(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            password_hash=password_hash,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user


