import random
import string
from uuid import uuid4

import pytest

from app.core.security import SecurityService
from app.db.database import get_db
from app.db.models import Order, OrderItem, Product, User


def create_random_products(db, count=3):
    products = []
    for _ in range(count):
        name = "Product " + "".join(random.choices(string.ascii_uppercase, k=5))
        sku = "SKU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        product = Product(
            id=uuid4(),
            name=name,
            description="Random description",
            price=round(random.uniform(10, 100), 2),
            sku=sku,
            inventory_count=random.randint(1, 50),
        )
        db.add(product)
        products.append(product)
    db.commit()
    return products


@pytest.fixture(scope="module")
def db():
    db = next(get_db())
    yield db


@pytest.fixture
def test_user(db):
    user = User(id=uuid4(), email="test@example.com", name="Test User", hashed_password="hashedpassword")
    db.add(user)
    db.commit()
    return user


def auth_header(user_id: str = None):
    service = SecurityService()
    token = service.create_access_token({"sub": user_id or str(uuid4())})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function", autouse=True)
def clean_orders_db(db):
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(User).delete()
    db.query(Product).delete()
    db.commit()
    yield
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(User).delete()
    db.query(Product).delete()
    db.commit()
