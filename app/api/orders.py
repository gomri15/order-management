from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from app.auth.dependencies import get_current_user
from app.core.errors import NotFoundError
from app.db.database import get_db
from app.schemas.orders import GetOrdersQueryParams, OrderCreate, OrderItemRead, OrderRead, OrderUpdate
from app.services.orders import OrderService
from sqlalchemy.orm import Session


router = APIRouter()


class OrderAPI:
    @staticmethod
    @router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
    def create_order(
        data: OrderCreate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
    ) -> OrderRead:
        service = OrderService(db)
        return service.create_order(user.id, data)

    @staticmethod
    @router.get("/admin", response_model=list[OrderRead])
    def get_all_orders(
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
        filters: GetOrdersQueryParams = Depends()
    ) -> list[OrderRead]:
        order_service = OrderService(db)
        try:
            return order_service.get_all_orders(filters=filters)

        except NotFoundError:
            raise HTTPException(status_code=404, detail="No orders found for this user")

    @staticmethod
    @router.get("/{order_id}/items", response_model=list[OrderItemRead])
    def get_order_items(
        order_id: str,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
    ) -> OrderRead:
        service = OrderService(db)
        order = service.get_order_items(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @staticmethod
    @router.get("/{order_id}", response_model=OrderRead)
    def get_order(
        order_id: UUID4,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
    ) -> OrderRead:
        service = OrderService(db)
        order = service.get_order(order_id, user_id=user.id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @staticmethod
    @router.put("/{order_id}", response_model=OrderRead)
    def update_order(
        order_id: str,
        data: OrderUpdate,
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
    ) -> OrderRead:
        service = OrderService(db)
        order = service.get_order(order_id, user.id)
        print(order)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        try:
            return service.update_order(order, data)  # Assuming update_order method exists in OrderService

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    @router.get("/", response_model=list[OrderRead])
    def get_user_orders(
        db: Session = Depends(get_db),
        filters: GetOrdersQueryParams = Depends(),
        user=Depends(get_current_user),
    ) -> list[OrderRead]:
        order_service = OrderService(db)
        try:
            return order_service.get_orders_by_user(user_id=user.id, filters=filters)

        except NotFoundError:
            raise HTTPException(status_code=404, detail="No orders found for this user")
