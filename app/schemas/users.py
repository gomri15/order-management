from pydantic import BaseModel, EmailStr

# Schema for User Registration & Response


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # Allows converting SQLAlchemy models to Pydantic


class UserLogin(BaseModel):
    email: EmailStr
    password: str
