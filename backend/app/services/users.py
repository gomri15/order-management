import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NoChangeError
from app.core.security import SecurityService
from app.db.models import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session, security_service: SecurityService):
        self.db = db
        self.security_service = security_service

    def create_user(self, user_data: UserCreate) -> User:
        hashed_pw = self.security_service.hash_password(user_data.password)
        new_user = User(email=user_data.email, name=user_data.name, hashed_password=hashed_pw)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, login_data: UserLogin) -> str:
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user or not self.security_service.verify_password(login_data.password, user.hashed_password):
            return None
        return self.security_service.create_access_token({"sub": str(user.id)})

    def update_user(self, user_id: str, updated_data: UserUpdate):
        user_to_update = self.db.query(User).filter(User.id == user_id).first()
        if user_to_update.email == updated_data.email \
                and user_to_update.name == updated_data.name:
            raise NoChangeError("No changes detected in user data.")

        # TODO: can be a separate method to check the new data is the same or not
        user_to_update.name = updated_data.name
        user_to_update.email = updated_data.email
        self.db.commit()
        self.db.refresh(user_to_update)

    def get_user(self, user_id: UUID) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def is_user_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).filter(User.deleted == False).offset(skip).limit(limit).all()

    def delete_user(self, user_id):
        user_to_delete = self.db.query(User).filter(User.id == user_id).first()
        if user_to_delete.deleted:
            raise NoChangeError("User already deleted.")

        if not user_to_delete:
            raise NoChangeError("User not found.")

        user_to_delete.deleted = True
        logger.info(f"Deleting user {user_id}")
        self.db.commit()
        self.db.refresh(user_to_delete)
