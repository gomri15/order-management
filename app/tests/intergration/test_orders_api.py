from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.enums.order_status import OrderStatusEnum
from app.main import app
from app.schemas.orders import OrderCreate, OrderItemRead, OrderUpdate
from app.tests.intergration.conftest import auth_header, create_random_products
from urllib.parse import quote

client = TestClient(app)


def assert_order_response(order_response, expected_order, expected_items, expected_status_id=None, expected_user_id=None):
    """
    Generic function to assert order details in the response.
    """
    assert order_response["shipping_address"] == expected_order.shipping_address, "failed assert shipping_address"
    assert order_response["shipping_city"] == expected_order.shipping_city, "failed assert shipping_city"
    assert order_response["shipping_postal_code"] == expected_order.shipping_postal_code, "failed assert shipping_postal_code"
    assert order_response["shipping_country"] == expected_order.shipping_country, "failed assert shipping_country"
    if expected_status_id is not None:
        assert order_response["status_id"] == expected_status_id, "failed assert status_id"
    if expected_user_id is not None:
        assert order_response["user_id"] == expected_user_id, "failed assert user_id"
    assert len(order_response["items"]) == len(expected_items)
    expected_product_ids = [str(p.product_id) for p in expected_items]
    actual_product_ids = [item["product_id"] for item in order_response["items"]]
    assert set(actual_product_ids) == set(expected_product_ids), (
        f"Product IDs mismatch. Actual: {actual_product_ids}, Actual: {expected_product_ids}"
    )
    for item, expected_item in zip(order_response["items"], expected_items):
        assert item["quantity"] == expected_item.quantity, (
            f"Quantity mismatch for product_id {item['product_id']}. "
            f"Actual: {item['quantity']}, Expected: {expected_item.quantity}"
        )


def test_create_order_success(test_user, db):
    products = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    response = client.post(
        "/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )

    assert response.status_code == 201
    assert_order_response(response.json(), order_payload, items, expected_status_id=1)


def test_get_order_success(test_user, db):
    products = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    # Create an order first
    response = client.post(
        "/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )
    order_id = response.json()["id"]

    # Now get the order
    response = client.get(
        f"/orders/{order_id}",
        headers=auth_header(str(test_user.id))
    )

    assert response.status_code == 200
    assert_order_response(response.json(), order_payload, items, expected_status_id=1, expected_user_id=str(test_user.id))


def test_order_update(test_user, db):
    products = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    # Create an order first
    response = client.post(
        "/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )
    order_id = response.json()["id"]

    # Update the order
    updated_items = [OrderItemRead(product_id=p.id, quantity=3, unit_price=2.3) for p in products]
    updated_order_payload = OrderUpdate(
        items=updated_items,
        shipping_address="456 Updated St",
        shipping_city="Updated City",
        shipping_postal_code="12345",
        shipping_country="Updated Country",
        status_id=2  # Assuming 2 is a valid status ID for the test
    )

    response = client.put(
        f"/orders/{order_id}",
        headers=auth_header(str(test_user.id)),
        json=updated_order_payload.model_dump(mode="json")
    )

    assert response.status_code == 200
    assert_order_response(response.json(), updated_order_payload, updated_items, expected_status_id=2)


def test_get_users_orders(test_user, db):
    products = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    # Create an order first
    response = client.post(
        "/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )
    order_id = response.json()["id"]

    # Now get the user's orders
    response = client.get(
        f"/orders",
        headers=auth_header(str(test_user.id))
    )

    assert response.status_code == 200
    assert len(response.json()) > 0
    assert any(order["id"] == order_id for order in response.json())


def test_no_orders_found_for_user(test_user, db):
    # Attempt to get orders for a user with no orders
    response = client.get(
        f"/orders",
        headers=auth_header(str(test_user.id))
    )

    assert response.status_code == 200
    assert response.json() == []


def test_filter_users_orders_by_status_id(test_user, db):
    products1 = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products1]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    order_payload2 = order_payload.model_copy()

    create_response1 = client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )

    order_id1 = create_response1.json()["id"]

    # Update the order
    updated_items = [OrderItemRead(product_id=p.id, quantity=3, unit_price=44) for p in products1]
    updated_status_id = OrderStatusEnum.PROCESSED.value
    updated_order_payload = OrderUpdate(
        items=updated_items,
        shipping_address="456 Updated St",
        shipping_city="Updated City",
        shipping_postal_code="12345",
        shipping_country="Updated Country",
        status_id=updated_status_id  # Assuming 2 is a valid status ID for the test
    )

    get_response = client.put(
        f"/orders/{order_id1}",
        headers=auth_header(str(test_user.id)),
        json=updated_order_payload.model_dump(mode="json")
    )

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload2.model_dump(mode="json")
    )

    # Now get the user's orders
    get_response = client.get(
        f"/orders?statusId={updated_status_id}",
        headers=auth_header(str(test_user.id))
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert_order_response(
        get_response.json()[0],
        updated_order_payload,
        updated_items,
        expected_status_id=updated_status_id
    )


def test_filter_users_orders_by_created_at_bigger_than(test_user, db):
    products1 = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products1]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    products2 = create_random_products(db, count=3)
    items2 = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products2]
    order_payload2 = OrderCreate(
        items=items2,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )

    current_time = datetime.now(timezone.utc)
    timestamp = quote(current_time.isoformat())

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload2.model_dump(mode="json")
    )

    # Now get the user's orders
    get_response = client.get(
        f"/orders?createdAt={timestamp}",
        headers=auth_header(str(test_user.id))
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert_order_response(
        get_response.json()[0],
        order_payload2,
        items2,
    )


def test_get_limit(test_user, db):
    products1 = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products1]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    products2 = create_random_products(db, count=3)
    items2 = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products2]
    order_payload2 = OrderCreate(
        items=items2,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload2.model_dump(mode="json")
    )

    # Now get the user's orders
    get_response = client.get(
        f"/orders?limit=1",
        headers=auth_header(str(test_user.id))
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1


def test_order_multiple_filters(test_user, db):
    products1 = create_random_products(db, count=3)
    items = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products1]
    order_payload = OrderCreate(
        items=items,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    products2 = create_random_products(db, count=3)
    items2 = [OrderItemRead(product_id=p.id, quantity=2, unit_price=2.3) for p in products2]
    order_payload2 = OrderCreate(
        items=items2,
        shipping_address="123 Python Way",
        shipping_city="Testville",
        shipping_postal_code="45678",
        shipping_country="Testland"
    )

    current_time = datetime.now(timezone.utc)
    timestamp = quote(current_time.isoformat())

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload.model_dump(mode="json")
    )

    client.post(
        f"/orders",
        headers=auth_header(str(test_user.id)),
        json=order_payload2.model_dump(mode="json")
    )

    # Now get the user's orders
    get_response = client.get(
        f"/orders?statusId=1&createdAt={timestamp}&limit=1",
        headers=auth_header(str(test_user.id))
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert_order_response(
        get_response.json()[0],
        order_payload2,
        items2,
        expected_status_id=1
    )
