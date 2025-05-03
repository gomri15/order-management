import random
import uuid
from datetime import datetime, timezone

from bcrypt import hashpw, gensalt
from faker import Faker
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import User, Product, Order, OrderItem
from app.enums.order_status import OrderStatusEnum


def random_product_name():
    food_adj = ["spicy", "sweet", "savory", "creamy", "zesty"]
    food_noun = ["noodles", "burger", "soup", "pancakes", "tart"]

    clothing_adj = ["warm", "soft", "cozy", "light", "casual"]
    clothing_noun = ["sweater", "jacket", "shirt", "scarf", "hat"]

    food_item = f"{random.choice(food_adj)} {random.choice(food_noun)}"
    clothing_item = f"{random.choice(clothing_adj)} {random.choice(clothing_noun)}"

    return food_item, clothing_item


faker = Faker()


def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')


def seed_database():
    db: Session = SessionLocal()

    try:
        # Seed users
        user1 = User(
            id=uuid.uuid4(),
            name=faker.name(),
            email=faker.email(),
            hashed_password=get_password_hash("password123"),
            deleted=False
        )
        user2 = User(
            id=uuid.uuid4(),
            name=faker.name(),
            email=faker.email(),
            hashed_password=get_password_hash("securepassword"),
            deleted=False
        )
        db.add_all([user1, user2])
        db.commit()

        # Seed products
        product1 = Product(
            id=uuid.uuid4(),
            name=random_product_name(),
            price=10.99,
            inventory_count=100,
            sku=faker.unique.ean(length=8)
        )
        product2 = Product(
            id=uuid.uuid4(),
            name=random_product_name(),
            price=20.99,
            inventory_count=50,
            sku=faker.unique.ean(length=8)
        )
        product3 = Product(
            id=uuid.uuid4(),
            name=random_product_name(),
            price=15.99,
            inventory_count=75,
            sku=faker.unique.ean(length=8)
        )
        db.add_all([product1, product2, product3])
        db.commit()

        # Seed orders
        order1 = Order(
            id=uuid.uuid4(),
            user_id=user1.id,
            status_id=OrderStatusEnum.PROCESSED.value,
            created_at=datetime.now(timezone.utc),
            shipping_address="123 Test St",
            shipping_city="Test City",
            shipping_postal_code="12345",
            shipping_country="Testland"
        )
        order2 = Order(
            id=uuid.uuid4(),
            user_id=user2.id,
            status_id=OrderStatusEnum.PENDING.value,
            created_at=datetime.now(timezone.utc),
            shipping_address="456 Another St",
            shipping_city="Another City",
            shipping_postal_code="67890",
            shipping_country="Anotherland"
        )
        db.add_all([order1, order2])
        db.commit()

        # Seed order items
        order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=2, unit_price=product1.price,
                                product_display_name=product1.name)
        order_item2 = OrderItem(order_id=order1.id, product_id=product2.id, quantity=1, unit_price=product2.price,
                                product_display_name=product2.name)
        order_item3 = OrderItem(order_id=order2.id, product_id=product3.id, quantity=3, unit_price=product3.price,
                                product_display_name=product3.name)
        db.add_all([order_item1, order_item2, order_item3])
        db.commit()

        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred while seeding the database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
