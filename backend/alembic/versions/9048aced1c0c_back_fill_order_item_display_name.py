"""back fill order item display name

Revision ID: 9048aced1c0c
Revises: 364024017a28
Create Date: 2025-05-01 06:26:28.137144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9048aced1c0c'
down_revision: Union[str, None] = '364024017a28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        UPDATE order_items
        SET product_display_name = products.name
        FROM products
        WHERE order_items.product_id = products.id
        AND order_items.product_display_name IS NULL;
    """)


def downgrade():
    # Optional: only do this if safe to null it out
    op.execute("""
        UPDATE order_items
        SET product_display_name = NULL
        WHERE product_display_name IS NOT NULL;
    """)
