from typing import List
import uuid

from app.auth.dependencies import get_current_user
from app.core.errors import NoChangeError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserCreate, UserResponse, UserLogin, UserUpdate
from app.services.orders import OrderService, get_order_service
from app.services.users import UserService
from app.core.security import get_security_service, SecurityService

router = APIRouter()


class UserAPI:
    @staticmethod
    @router.post("/register",
                 response_model=UserResponse,
                 status_code=status.HTTP_201_CREATED)
    def register_user(
            user: UserCreate,
            db: Session = Depends(get_db),
            security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        existing_user = user_service.is_user_exists(user.email)
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

    @staticmethod
    @router.put("/{user_id}")
    def update_user(
            user_id: str,
            update_data: UserUpdate,
            db: Session = Depends(get_db),
            security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        try:
            user_service.update_user(user_id, update_data)

        except NoChangeError:
            raise HTTPException(status_code=200, detail="No changes to update")

    @staticmethod
    @router.get("/", response_model=List[UserResponse])
    # TODO: add filtering
    def get_users(
            db: Session = Depends(get_db),
            security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        return user_service.get_users()

    @staticmethod
    @router.get("/current", response_model=UserResponse)
    def fetch_current_user(
            user: User = Depends(get_current_user)  # Assuming get_current_user is defined elsewhere
    ):
        return user

    @staticmethod
    @router.delete("/admin/{user_id}", response_model=dict)
    def delete_users(
            user_id: str,
            db: Session = Depends(get_db),
            security_service: SecurityService = Depends(get_security_service)
    ):
        user_service = UserService(db, security_service)
        user_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
