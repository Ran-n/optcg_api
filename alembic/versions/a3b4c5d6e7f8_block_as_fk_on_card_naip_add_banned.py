#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/05/21 13:15:15.195431
Revised: 2026/05/21 13:15:19.608122
"""

"""block as direct fk on card/naip, add image to block, add card_ban and banned_pair

Revision ID: a3b4c5d6e7f8
Revises: 75adbb637f38
Create Date: 2026-05-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a3b4c5d6e7f8"
down_revision: str | Sequence[str] | None = "75adbb637f38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS_DEFAULT = sa.text("(strftime('%Y-%m-%d %H:%M:%f', 'now'))")


def upgrade() -> None:
    # block: add image_fk (batch required for FK constraints in SQLite)
    with op.batch_alter_table("block") as batch_op:
        batch_op.add_column(sa.Column("image_fk", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_block_image_fk", "image", ["image_fk"], ["id"])

    # card: add block_fk; drop card_block junction
    op.drop_index("ix_card_block_card_fk", table_name="card_block")
    op.drop_index("ix_card_block_block_fk", table_name="card_block")
    op.drop_table("card_block")
    with op.batch_alter_table("card") as batch_op:
        batch_op.add_column(sa.Column("block_fk", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_card_block_fk", "block", ["block_fk"], ["id"])

    # naip: add block_fk; drop naip_block junction
    op.drop_index("ix_naip_block_naip_fk", table_name="naip_block")
    op.drop_index("ix_naip_block_block_fk", table_name="naip_block")
    op.drop_table("naip_block")
    with op.batch_alter_table("naip") as batch_op:
        batch_op.add_column(sa.Column("block_fk", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_naip_block_fk", "block", ["block_fk"], ["id"])

    # card_ban: per-card ban, scoped to a format or all formats (format_fk NULL)
    op.create_table(
        "card_ban",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("card_fk", sa.Integer(), sa.ForeignKey("card.id"), nullable=False),
        sa.Column("format_fk", sa.Integer(), sa.ForeignKey("format.id"), nullable=True),
        sa.UniqueConstraint("card_fk", "format_fk"),
    )
    op.create_index("ix_card_ban_card_fk", "card_ban", ["card_fk"])
    op.create_index("ix_card_ban_format_fk", "card_ban", ["format_fk"])

    # banned_pair: two-card combo ban, scoped to a format or all formats (format_fk NULL)
    op.create_table(
        "banned_pair",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("card_a_fk", sa.Integer(), sa.ForeignKey("card.id"), nullable=False),
        sa.Column("card_b_fk", sa.Integer(), sa.ForeignKey("card.id"), nullable=False),
        sa.Column("format_fk", sa.Integer(), sa.ForeignKey("format.id"), nullable=True),
        sa.UniqueConstraint("card_a_fk", "card_b_fk", "format_fk"),
        sa.CheckConstraint("card_a_fk < card_b_fk", name="ck_banned_pair_ordered"),
    )
    op.create_index("ix_banned_pair_card_a_fk", "banned_pair", ["card_a_fk"])
    op.create_index("ix_banned_pair_card_b_fk", "banned_pair", ["card_b_fk"])
    op.create_index("ix_banned_pair_format_fk", "banned_pair", ["format_fk"])

    # triggers
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_block_update
        AFTER UPDATE ON block
        FOR EACH ROW
        WHEN NEW.updated_ts IS OLD.updated_ts
        BEGIN
            UPDATE block SET updated_ts = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE id = NEW.id;
        END
    """)
    )
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_card_ban_update
        AFTER UPDATE ON card_ban
        FOR EACH ROW
        WHEN NEW.updated_ts IS OLD.updated_ts
        BEGIN
            UPDATE card_ban SET updated_ts = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE id = NEW.id;
        END
    """)
    )
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_banned_pair_update
        AFTER UPDATE ON banned_pair
        FOR EACH ROW
        WHEN NEW.updated_ts IS OLD.updated_ts
        BEGIN
            UPDATE banned_pair SET updated_ts = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE id = NEW.id;
        END
    """)
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_banned_pair_update"))
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_card_ban_update"))
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_block_update"))

    op.drop_index("ix_banned_pair_format_fk", table_name="banned_pair")
    op.drop_index("ix_banned_pair_card_b_fk", table_name="banned_pair")
    op.drop_index("ix_banned_pair_card_a_fk", table_name="banned_pair")
    op.drop_table("banned_pair")

    op.drop_index("ix_card_ban_format_fk", table_name="card_ban")
    op.drop_index("ix_card_ban_card_fk", table_name="card_ban")
    op.drop_table("card_ban")

    with op.batch_alter_table("naip") as batch_op:
        batch_op.drop_constraint("fk_naip_block_fk", type_="foreignkey")
        batch_op.drop_column("block_fk")
    op.create_table(
        "naip_block",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("naip_fk", sa.Integer(), sa.ForeignKey("naip.id"), nullable=False),
        sa.Column("block_fk", sa.Integer(), sa.ForeignKey("block.id"), nullable=False),
        sa.UniqueConstraint("naip_fk", "block_fk"),
    )
    op.create_index("ix_naip_block_naip_fk", "naip_block", ["naip_fk"])
    op.create_index("ix_naip_block_block_fk", "naip_block", ["block_fk"])

    with op.batch_alter_table("card") as batch_op:
        batch_op.drop_constraint("fk_card_block_fk", type_="foreignkey")
        batch_op.drop_column("block_fk")
    op.create_table(
        "card_block",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("card_fk", sa.Integer(), sa.ForeignKey("card.id"), nullable=False),
        sa.Column("block_fk", sa.Integer(), sa.ForeignKey("block.id"), nullable=False),
        sa.UniqueConstraint("card_fk", "block_fk"),
    )
    op.create_index("ix_card_block_card_fk", "card_block", ["card_fk"])
    op.create_index("ix_card_block_block_fk", "card_block", ["block_fk"])

    with op.batch_alter_table("block") as batch_op:
        batch_op.drop_constraint("fk_block_image_fk", type_="foreignkey")
        batch_op.drop_column("image_fk")
