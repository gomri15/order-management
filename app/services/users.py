from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.users import UserCreate, UserLogin
from app.core.security import SecurityService

class UserService:
    def __init__(self, db: Session, security_service: SecurityService):
        self.db = db
        self.security_service = security_service

    def create_user(self, user_data: UserCreate):
        hashed_pw = self.security_service.hash_password(user_data.password)
        new_user = User(email=user_data.email, name=user_data.name, hashed_password=hashed_pw)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, login_data: UserLogin):
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user or not self.security_service.verify_password(login_data.password, user.hashed_password):
            return None
        return self.security_service.create_access_token({"sub": user.email})
