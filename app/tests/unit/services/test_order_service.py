import uuid
from app.consts.order_status import ORDER_STATUS_NAME_TO_ID
from app.db.models import Order
from app.enums.order_status import OrderStatusEnum
from app.schemas.orders import GetOrdersQueryParams, OrderCreate
from app.schemas.products import ProductCreate
from app.services.orders import OrderService
from app.services.products import ProductService


def test_order_service_create_order(mock_db_session):
    order_create = OrderCreate(
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[
            {
                "product_id": uuid.uuid4(),
                "quantity": 2,
            }
        ],
    )
    user_id = uuid.uuid4()
    service = OrderService(mock_db_session)

    result = service.create_order(user_id, order_create)

    assert mock_db_session.add.call_count == 2
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert isinstance(result, Order)


def test_user_cant_see_other_user_orders(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.DELIVERED])
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 0


def test_get_orders_by_user(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PROCESSED])
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 1
    assert results[0].status_id == ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PROCESSED]
    assert str(results[0].user_id) == str(data["test_user_id"])


def test_get_orders_by_user_limit_zero(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.DELIVERED],
                                   limit=0)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 0


def test_get_orders_by_user_with_unknown_user_id(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.DELIVERED],
                                   limit=1)
    results = service.get_orders_by_user(user_id=uuid.uuid4(), filters=filters)

    assert len(results) == 0


def test_get_orders_limit(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)
    product_service = ProductService(db=db)
    product_id = product_service.create_product(
        ProductCreate(
            name="Test Product",
            description="Test Description",
            price=100.0,
            inventory_count=10,
            sku="TESTSKU123",
        )
    ).id
    service.create_order(
        user_id=data["test_user_id"],
        data=OrderCreate(
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_postal_code="12345",
            shipping_country="Testland",
            items=[
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        ),
    )

    filters = GetOrdersQueryParams(status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PROCESSED],
                                   limit=1)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 1
    assert results[0].status_id == ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PROCESSED]
    assert str(results[0].user_id) == str(data["test_user_id"])
