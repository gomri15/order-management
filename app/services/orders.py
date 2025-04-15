from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.errors import NotFoundError
from app.db.models import Order, OrderItem, OrderStatus, Product
from app.enums.order_status import OrderStatusEnum
from app.schemas.orders import GetOrdersQueryParams, OrderCreate, OrderUpdate


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    # TODO: make sure there is item in order before creating order
    def create_order(self, user_id: UUID, data: OrderCreate) -> Order:
        status = self.db.query(OrderStatus).filter_by(name=OrderStatusEnum.PENDING).first()
        if not status:
            raise NotFoundError("Default order status 'pending' not found")

        order = Order(
            user_id=user_id,
            status_id=status.id,
            shipping_address=data.shipping_address,
            shipping_city=data.shipping_city,
            shipping_postal_code=data.shipping_postal_code,
            shipping_country=data.shipping_country,
        )
        self.db.add(order)
        self.db.flush()  # so order.id is available

        for item in data.items:
            product = self.db.query(Product).filter_by(id=item.product_id).first()

            if not product:
                raise NotFoundError(f"Product {item.product_id} not found")

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: str, user_id: UUID) -> Order:
        order = self.db.query(Order).filter_by(id=order_id, user_id=user_id).first()

        if not order:
            raise NotFoundError("Order not found")

        return order

    def get_order_items(self, order_id: UUID) -> list[OrderItem]:
        order_items = self.db.query(OrderItem).filter_by(order_id=order_id).all()

        if not order_items:
            raise NotFoundError(f"Order items not found, {order_id}")

        return order_items

    def get_all_orders(self, filters: GetOrdersQueryParams) -> List[Order]:
        try:
            query = self.db.query(Order)
            query = self._query_orders_by_filter(filters, query)
            return query.all()
        except Exception as e:
            raise ValueError(f"Error fetching all orders: {str(e)}")

    def get_orders_by_user(self, user_id: UUID, filters: GetOrdersQueryParams) -> List[Order]:
        try:
            query = self.db.query(Order).filter(Order.user_id == user_id)
            query = self._query_orders_by_filter(filters, query)
            return query.all()
        except Exception as e:
            raise ValueError(f"Error fetching orders for user {user_id}: {str(e)}")

    def _query_orders_by_filter(self, filters, query):
        if filters.status_id:
            query = query.filter(Order.status_id == filters.status_id)

        if filters.created_at:
            query = query.filter(Order.created_at >= filters.created_at)

        query = query.order_by(Order.created_at.desc())

        if filters.limit:
            query = query.limit(filters.limit)
        return query

    def update_order(self, order: Order, data: OrderUpdate) -> Order:
        order.shipping_address = data.shipping_address
        order.shipping_city = data.shipping_city
        order.shipping_postal_code = data.shipping_postal_code
        order.shipping_country = data.shipping_country
        order.status_id = data.status_id

        for item in data.items:
            existing_item = self.db.query(OrderItem).filter_by(order_id=order.id, product_id=item.product_id).first()

            if existing_item:
                existing_item.quantity = item.quantity

            else:
                new_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=existing_item.unit_price,
                )
                self.db.add(new_item)

        self.db.commit()
        self.db.refresh(order)
        return order
