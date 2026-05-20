"""add naip.serial_max and naip_serial table

Revision ID: d67a59a0943a
Revises: h2i3j4k5l6m7
Create Date: 2026-05-20 13:28:01.900399

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d67a59a0943a"
down_revision: str | Sequence[str] | None = "h2i3j4k5l6m7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS_DEFAULT = sa.text("(strftime('%Y-%m-%d %H:%M:%f', 'now'))")


def upgrade() -> None:
    op.add_column("naip", sa.Column("serial_max", sa.Integer(), nullable=True))

    op.create_table(
        "naip_serial",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("naip_fk", sa.Integer(), sa.ForeignKey("naip.id"), nullable=False),
        sa.Column("serial_number", sa.Integer(), nullable=False),
        sa.Column("image_fk", sa.Integer(), sa.ForeignKey("image.id"), nullable=True),
        sa.UniqueConstraint("naip_fk", "serial_number"),
        sa.CheckConstraint("serial_number >= 1", name="ck_naip_serial_number_positive"),
    )
    op.create_index("ix_naip_serial_naip_fk", "naip_serial", ["naip_fk"])


def downgrade() -> None:
    op.drop_index("ix_naip_serial_naip_fk", table_name="naip_serial")
    op.drop_table("naip_serial")
    op.drop_column("naip", "serial_max")
