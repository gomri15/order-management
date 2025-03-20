from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


# Enum for Order Status
class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

# Association table for many-to-many relationship between Orders and Products
order_items_table = Table(
    "order_items",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),
)


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)

    orders = relationship("Order", back_populates="user")

# Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    inventory_count = Column(Integer, nullable=False)

    orders = relationship("Order", secondary=order_items_table, back_populates="products")

# Order Model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus, name="orderstatus"), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="orders")
    products = relationship("Product", secondary=order_items_table, back_populates="orders")
