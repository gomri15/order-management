from datetime import UTC, datetime, timezone
import logging
from time import sleep
import uuid

import pytest
from app.core.errors import NotFoundError
from app.db.models import Order
from app.enums.order_status import OrderStatusEnum
from app.schemas.orders import GetOrdersQueryParams, OrderCreate, OrderItemCreate, OrderItemRead, OrderUpdate
from app.services.orders import OrderService

order_service_test_logger = logging.getLogger(__name__)


def test_order_service_create_order(mock_db_session):
    order_create = OrderCreate(
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[OrderItemCreate(
            product_id=uuid.uuid4(),
            quantity=2,
            unit_price=100.0,
        )],
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

    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.DELIVERED.value)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 0


def test_get_orders_by_user(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.PROCESSED.value)
    product_id = data["products"][0].id
    product_price = data["products"][0].price
    order_id = service.create_order(
        user_id=data["test_user_id"],
        data=OrderCreate(
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_postal_code="12345",
            shipping_country="Testland",
            items=[OrderItemCreate(
                product_id=product_id,
                quantity=2,
                unit_price=product_price,
            )],
        ),
    ).id
    order_update = OrderUpdate(status_id=OrderStatusEnum.PROCESSED.value,
                               shipping_address="456 Test St",
                               shipping_city="Test City",
                               shipping_postal_code="54321",
                               shipping_country="Testland",
                               items=[OrderItemCreate(product_id=data["products"][0].id,
                                                      quantity=2,
                                                      unit_price=data["products"][0].price)]
                               )
    order = service.get_order(order_id=order_id, user_id=data["test_user_id"])
    service.update_order(order=order, data=order_update)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 1
    assert results[0].status_id == OrderStatusEnum.PROCESSED.value
    assert str(results[0].user_id) == str(data["test_user_id"])


def test_get_orders_by_user_limit_zero(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.DELIVERED.value,
                                   limit=0)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 0


def test_get_orders_by_user_with_unknown_user_id(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.DELIVERED.value,
                                   limit=1)
    results = service.get_orders_by_user(user_id=uuid.uuid4(), filters=filters)

    assert len(results) == 0


def test_get_orders_limit(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)
    product_id = data["products"][0].id
    order_id = service.create_order(
        user_id=data["test_user_id"],
        data=OrderCreate(
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_postal_code="12345",
            shipping_country="Testland",
            items=[OrderItemCreate(
                product_id=product_id,
                quantity=2,
                unit_price=100.0,
            )],
        ),
    ).id

    order = service.get_order(order_id=order_id, user_id=data["test_user_id"])
    order_update = OrderUpdate(status_id=OrderStatusEnum.PROCESSED.value,
                               shipping_address="456 Test St",
                               shipping_city="Test City",
                               shipping_postal_code="54321",
                               shipping_country="Testland",
                               items=[OrderItemCreate(product_id=data["products"][0].id,
                                                      quantity=2,
                                                      unit_price=data["products"][0].price)]
                               )
    service.update_order(order=order, data=order_update)
    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.PROCESSED.value,
                                   limit=1)
    results = service.get_orders_by_user(user_id=data["test_user_id"], filters=filters)

    assert len(results) == 1
    assert results[0].status_id == OrderStatusEnum.PROCESSED.value
    assert str(results[0].user_id) == str(data["test_user_id"])


def test_get_order_items(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    order_id = data["orders"][0].id
    items = service.get_order_items(order_id=order_id)
    assert len(items) == 1
    assert str(items[0].order_id) == str(order_id)


def test_get_order_items_raises_for_order_with_no_items(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db=db)

    order_id = uuid.uuid4()
    service.create_order(user_id=data["test_user_id"], data=OrderCreate(
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[],
    ))

    with pytest.raises(NotFoundError) as excinfo:
        service.get_order_items(order_id=order_id)


def test_get_order_items_raises_for_nonexistent_order(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db)
    with pytest.raises(NotFoundError):
        service.get_order_items(uuid.uuid4())


def test_get_all_orders_with_multiple_filters(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db)

    now = datetime.now(tz=UTC)
    order_id = service.create_order(user_id=data["test_user_id"], data=OrderCreate(
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[OrderItemCreate(product_id=data["products"][0].id,
                               quantity=2,
                               unit_price=data["products"][0].price)],
    )).id
    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.PENDING.value,
                                   created_at=now)

    results = service.get_all_orders(filters)

    assert len(results) == 1
    assert results[0].status_id == OrderStatusEnum.PENDING.value
    assert str(results[0].id) == str(order_id)


def test_get_all_orders_with_status_id(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db)

    order_id = service.create_order(user_id=data["test_user_id"], data=OrderCreate(
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[OrderItemCreate(product_id=data["products"][0].id,
                               quantity=2,
                               unit_price=data["products"][0].price)],
    )).id

    order = service.get_order(order_id=order_id, user_id=data["test_user_id"])
    order_update = OrderUpdate(status_id=OrderStatusEnum.PROCESSED.value,
                               shipping_address="456 Test St",
                               shipping_city="Test City",
                               shipping_postal_code="54321",
                               shipping_country="Testland",
                               items=[OrderItemCreate(product_id=data["products"][0].id,
                                                      quantity=2,
                                                      unit_price=data["products"][0].price)]
                               )
    service.update_order(order=order, data=order_update)
    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.PROCESSED.value)

    results = service.get_all_orders(filters)

    assert len(results) == 1
    assert results[0].status_id == OrderStatusEnum.PROCESSED.value
    assert str(results[0].id) == str(order_id)


def test_get_all_orders_with_limit_order_desc(seeded_test_db):
    db, data = seeded_test_db
    service = OrderService(db)
    pre_create_time = datetime.now(tz=UTC)
    sleep(0.15)
    service.create_order(user_id=data["test_user_id"], data=OrderCreate(
        shipping_address="555 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="Testland",
        items=[OrderItemCreate(product_id=data["products"][0].id,
                               quantity=2,
                               unit_price=data["products"][0].price)],
    )).id

    filters = GetOrdersQueryParams(status_id=OrderStatusEnum.PENDING.value,
                                   limit=1)
    results = service.get_all_orders(filters)
    new_order_created_at = results[0].created_at.astimezone(timezone.utc)

    assert len(results) == 1
    assert new_order_created_at > pre_create_time
    assert results[0].status_id == OrderStatusEnum.PENDING.value
