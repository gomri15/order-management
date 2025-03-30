from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
