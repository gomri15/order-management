"""remove order_status table, add enum status to orders

Revision ID: e7d756a6c8e9
Revises: d960ad37b729
Create Date: 2025-04-16 05:23:55.734510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7d756a6c8e9'
down_revision: Union[str, None] = 'd960ad37b729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Drop foreign key constraint
    op.drop_constraint('orders_status_id_fkey', 'orders', type_='foreignkey')

    # 2. Optionally rename the column (if renaming to `status`)
    # op.alter_column('orders', 'status_id', new_column_name='status')

    # 3. Drop the `order_statuses` table
    op.drop_table('order_statuses')


def downgrade():
    # 1. Recreate the `order_statuses` table
    op.create_table(
        'order_statuses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String)
    )

    # 2. Optionally rename column back if it was renamed
    # op.alter_column('orders', 'status', new_column_name='status_id')

    # 3. Recreate the foreign key constraint
    op.create_foreign_key(
        'orders_status_id_fkey',
        'orders',
        'order_statuses',
        ['status_id'],
        ['id']
    )
