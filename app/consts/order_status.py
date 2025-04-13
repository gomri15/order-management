from app.enums.order_status import OrderStatusEnum


ORDER_STATUS_NAME_TO_ID = {
    OrderStatusEnum.PENDING: 1,
    OrderStatusEnum.PROCESSED: 2,
    OrderStatusEnum.SHIPPED: 3,
    OrderStatusEnum.DELIVERED: 4,
    OrderStatusEnum.CANCELED: 5,
}
