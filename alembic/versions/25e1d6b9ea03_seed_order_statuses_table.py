"""seed order_statuses table

Revision ID: 25e1d6b9ea03
Revises: 765959927373
Create Date: 2025-03-30 05:14:49.036796

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '25e1d6b9ea03'
down_revision: Union[str, None] = '765959927373'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

order_statuses_table = table(
    "order_statuses",
    column("id", Integer),
    column("name", String),
    column("description", String),
)


def upgrade():
    op.bulk_insert(order_statuses_table, [
        {"id": 1, "name": "pending", "description": "Order received and awaiting processing"},
        {"id": 2, "name": "processed", "description": "Order is being prepared"},
        {"id": 3, "name": "shipped", "description": "Order has been shipped"},
        {"id": 4, "name": "delivered", "description": "Order delivered to customer"},
        {"id": 5, "name": "canceled", "description": "Order was canceled"},
    ])


def downgrade():
    op.execute("DELETE FROM order_statuses WHERE id IN (1, 2, 3, 4, 5)")
