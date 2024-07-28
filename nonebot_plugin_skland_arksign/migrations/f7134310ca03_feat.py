"""feat

迁移 ID: f7134310ca03
父迁移: 486a6e0eed5b
创建时间: 2024-07-23 20:55:12.768283

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f7134310ca03"
down_revision: str | Sequence[str] | None = "486a6e0eed5b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "address",
                sa.JSON().with_variant(
                    postgresql.JSONB(astext_type=sa.Text()), "postgresql"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "status",
                sa.JSON().with_variant(
                    postgresql.JSONB(astext_type=sa.Text()), "postgresql"
                ),
                nullable=True,
            )
        )
        batch_op.drop_column("cred")
        batch_op.drop_constraint(batch_op.f("uq_skland_subscribe_note"), type_="unique")

    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("skland_subscribe", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cred", sa.VARCHAR(), nullable=False))
        batch_op.drop_column("status")
        batch_op.drop_column("address")
        batch_op.create_unique_constraint(batch_op.f("uq_skland_subscribe_note"), ["note"])

    # ### end Alembic commands ###