# app/schemas/product.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    inventory_count: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sku: Optional[str] = None
    inventory_count: Optional[int] = None

class ProductRead(ProductBase):
    id: UUID

    class Config:
        from_attributes = True  # required in Pydantic v2 to populate from SQLAlchemy model
