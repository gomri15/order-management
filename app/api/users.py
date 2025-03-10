from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.users import UserCreate, UserResponse, UserLogin
from app.services.users import UserService
from app.core.security import get_security_service, SecurityService

router = APIRouter()

class UserAPI:
    @staticmethod
    @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    def register_user(
        user: UserCreate,
        db: Session = Depends(get_db),
        security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return user_service.create_user(user)

    @staticmethod
    @router.post("/login", response_model=dict)
    def login_user(
        user: UserLogin,
        db: Session = Depends(get_db),
        security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        token = user_service.authenticate_user(user)
        if not token:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return {"access_token": token, "token_type": "bearer"}
