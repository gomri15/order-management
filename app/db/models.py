import uuid
from sqlalchemy import UUID, Column, Float, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    inventory_count = Column(Integer, default=0)
