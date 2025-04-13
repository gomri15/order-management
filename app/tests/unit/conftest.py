from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import SecurityService
from app.db.database import Base
from app.db.models import Order, OrderStatus
from app.enums.order_status import OrderStatusEnum
from app.consts.order_status import ORDER_STATUS_NAME_TO_ID
from app.services.users import UserService


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

    orders = seed_orders(db, test_user_id, other_user_id)
    db.commit()
    yield db, {"test_user_id": test_user_id, "other_user_id": other_user_id, "orders": orders}
    db.close()


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
