from enum import Enum, auto


class OrderStatusEnum(Enum):
    PENDING = auto()
    PROCESSED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELED = auto()
