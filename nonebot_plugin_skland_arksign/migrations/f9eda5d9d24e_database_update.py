"""database_update

Revision ID: f9eda5d9d24e
Revises: d89239244530
Create Date: 2023-12-17 10:43:59.367604

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = "f9eda5d9d24e"
down_revision = "d89239244530"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sendto", sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"), nullable=True
            )
        )
    op.execute("UPDATE skland_subscribe SET sendto = user")
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.alter_column("user", existing_type=sqlite.JSON(), nullable=True)



def downgrade() -> None:
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.alter_column("user", existing_type=sqlite.JSON(), nullable=False)

    op.execute("UPDATE skland_subscribe SET user = sendto")
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.drop_column("sendto")

