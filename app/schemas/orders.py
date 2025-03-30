from datetime import datetime
from pydantic import BaseModel, UUID4, Field, field_serializer
from typing import List, Optional


class OrderItemRead(BaseModel):
    product_id: UUID4
    quantity: int


class OrderBase(BaseModel):
    items: List[OrderItemRead]
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    status_id: int


class OrderItemCreate(BaseModel):
    product_id: UUID4
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderRead(OrderBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    items: List[OrderItemCreate]
    status_id: int

    model_config = {"from_attributes": True}


class GetOrdersQueryParams(BaseModel):
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    status_id: Optional[int] = Field(default=None, alias="statusId")

    class Config:
        populate_by_name = True
