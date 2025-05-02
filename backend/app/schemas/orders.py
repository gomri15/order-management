from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, UUID4, Field, ConfigDict

from app.enums.order_status import OrderStatusEnum


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID4
    quantity: int = Field(gt=0)
    unit_price: float


class OrderItemRead(BaseModel):
    id: UUID4
    product_id: UUID4
    quantity: int
    unit_price: float
    product_display_name: str


class OrderItemUpdate(BaseModel):
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    product_display_name: str


class OrderBase(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    status_id: int


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    created_at: datetime
    items: List[OrderItemRead]
    status_id: int
    total_price: float


class GetOrdersQueryParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    status_id: int = Field(OrderStatusEnum.PENDING.value, alias="statusId")
    limit: Optional[int] = Field(default=10)
