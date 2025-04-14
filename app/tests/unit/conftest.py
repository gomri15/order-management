from datetime import datetime
import logging
import random
from typing import List
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import SecurityService
from app.db.database import Base
from app.db.models import Order, OrderStatus, Product
from app.enums.order_status import OrderStatusEnum
from app.consts.order_status import ORDER_STATUS_NAME_TO_ID
from app.schemas.orders import OrderCreate
from app.schemas.products import ProductCreate
from app.services.orders import OrderService
from app.services.products import ProductService
from app.services.users import UserService
from faker import Faker

faker = Faker()


@pytest.fixture
def seeded_test_db():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Session()

    # Explicit test values
    test_user_id = uuid4()
    other_user_id = uuid4()
    seed_order_statuses(db)

    products = create_test_products(db)
    orders = create_test_orders(test_user_id, other_user_id, products, db)
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.debug("Orders seeded successfully.")
    logger.debug(f"Test user ID: {test_user_id}")
    logger.debug(f"Other user ID: {other_user_id}")
    logger.debug(f"Orders: {[order.id for order in orders]}")
    yield db, {"test_user_id": test_user_id,
               "other_user_id": other_user_id,
               "orders": orders,
               "products": products}
    db.close()


def create_test_orders(test_user_id, other_user_id, products: List[Product], db):
    order_service = OrderService(db=db)
    orders = []

    order1 = order_service.create_order(
        user_id=test_user_id,
        data=OrderCreate(
            shipping_address=faker.address(),
            shipping_city=faker.city(),
            shipping_country=faker.country(),
            shipping_postal_code=faker.postcode(),
            items=[
                {
                    "product_id": products[0].id,
                    "quantity": faker.random_int(min=1, max=5),
                    "unit_price": faker.random_number(digits=5, fix_len=True) / 100.0,
                }
            ],
        ),
    )
    orders.append(order1)

    order2 = order_service.create_order(
        user_id=test_user_id,
        data=OrderCreate(
            shipping_address=faker.address(),
            shipping_city=faker.city(),
            shipping_country=faker.country(),
            shipping_postal_code=faker.postcode(),
            items=[
                {
                    "product_id": products[0].id,
                    "quantity": faker.random_int(min=1, max=5),
                    "unit_price": faker.random_number(digits=5, fix_len=True) / 100.0,
                }
            ],
        ),
    )
    orders.append(order2)

    order3 = order_service.create_order(
        user_id=other_user_id,
        data=OrderCreate(
            shipping_address=faker.address(),
            shipping_city=faker.city(),
            shipping_country=faker.country(),
            shipping_postal_code=faker.postcode(),
            items=[
                {
                    "product_id": products[1].id,
                    "quantity": faker.random_int(min=1, max=5),
                    "unit_price": faker.random_number(digits=5, fix_len=True) / 100.0,
                }
            ],
        ),
    )
    orders.append(order3)

    return orders


def create_test_products(db, number_of_products: int = 3):
    products = []
    product_service = ProductService(db=db)
    for _ in range(number_of_products):
        product_data = ProductCreate(
            name=faker.word(),
            description=faker.text(max_nb_chars=50),
            price=faker.random_number(digits=5, fix_len=True) / 100.0,
            inventory_count=faker.random_int(min=10, max=100),
            sku=faker.unique.ean(length=8)
        )
        product = product_service.create_product(product_data=product_data)
        products.append(product)

    return products


def seed_orders(db, test_user_id, other_user_id):
    orders = [
        Order(id=uuid4(),
              user_id=test_user_id,
              status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PROCESSED],
              created_at=datetime(2024, 1, 1),
              shipping_address="123 Test St, Test City, TC 12345",
              shipping_city="Test City",
              shipping_country="Testland",
              shipping_postal_code="12345"),
        Order(id=uuid4(),
              user_id=test_user_id,
              status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.PENDING],
              created_at=datetime(2024, 2, 1),
              shipping_address="123 Test St, Test City, TC 12345",
              shipping_city="Test City",
              shipping_country="Testland",
              shipping_postal_code="12345"),
        Order(id=uuid4(),
              user_id=other_user_id,
              status_id=ORDER_STATUS_NAME_TO_ID[OrderStatusEnum.DELIVERED],
              created_at=datetime(2024, 3, 1),
              shipping_address="123 Test St, Test City, TC 12345",
              shipping_city="Test City",
              shipping_country="Testland",
              shipping_postal_code="12345"),
    ]
    db.add_all(orders)
    return orders


def seed_order_statuses(db):
    db.add_all([
        OrderStatus(id=1, name="pending", description="Waiting for processing"),
        OrderStatus(id=2, name="processed", description="Being packed"),
        OrderStatus(id=3, name="shipped", description="Shipped to customer"),
        OrderStatus(id=4, name="delivered", description="Delivered"),
        OrderStatus(id=5, name="canceled", description="Canceled by user"),
    ])


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.query = MagicMock()
    return session


@pytest.fixture
def user_service(mock_db_session, security_service):
    return UserService(db=mock_db_session, security_service=security_service)


@pytest.fixture
def security_service():
    return SecurityService()
