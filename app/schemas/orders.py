from datetime import datetime
from pydantic import BaseModel, UUID4, Field, model_validator
from typing import List, Optional

from app.consts.order_status import ORDER_STATUS_NAME_TO_ID


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
    status_id: int | None = None
    limit: Optional[int] = Field(default=10)

    @model_validator(mode="after")
    def validate_status_id(cls, values):
        if values.status_id is not None and values.status_id not in ORDER_STATUS_NAME_TO_ID.values():
            raise ValueError(f"Invalid status_id: {values.status_id}")
        return values

    class Config:
        populate_by_name = True
