#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/05/21 13:15:15.301836
Revised: 2026/05/21 13:15:19.824818
"""

"""drop naip_format, add set.block_fk, fix null-ban uniqueness, enforce serial_max

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-05-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b4c5d6e7f8a9"
down_revision: str | Sequence[str] | None = "a3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TS_DEFAULT = sa.text("(strftime('%Y-%m-%d %H:%M:%f', 'now'))")


def upgrade() -> None:
    # 1. Drop naip_format — format legality is card-level only (table may not exist in all envs)
    conn = op.get_bind()
    tables = [r[0] for r in conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()]
    if "naip_format" in tables:
        op.drop_index("ix_naip_format_naip_fk", table_name="naip_format")
        op.drop_index("ix_naip_format_format_fk", table_name="naip_format")
        op.execute(sa.text("DROP TRIGGER IF EXISTS trg_naip_format_update"))
        op.drop_table("naip_format")

    # 2. Add set.block_fk — a set belongs to exactly one block
    with op.batch_alter_table("set") as batch_op:
        batch_op.add_column(sa.Column("block_fk", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_set_block_fk", "block", ["block_fk"], ["id"])

    # 3a. CardBan NULL-safe uniqueness: prevent duplicate "global" (format_fk IS NULL) bans
    op.create_index(
        "ix_card_ban_global_unique",
        "card_ban",
        ["card_fk"],
        unique=True,
        sqlite_where=sa.text("format_fk IS NULL"),
    )

    # 3b. BannedPair NULL-safe uniqueness: prevent duplicate global pair bans
    op.create_index(
        "ix_banned_pair_global_unique",
        "banned_pair",
        ["card_a_fk", "card_b_fk"],
        unique=True,
        sqlite_where=sa.text("format_fk IS NULL"),
    )

    # 4. Enforce serial_number <= serial_max via BEFORE INSERT/UPDATE trigger on naip_serial.
    #    SQLite CHECK constraints cannot reference other tables, so a trigger is the only option.
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_naip_serial_check_max_insert
        BEFORE INSERT ON naip_serial
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, 'serial_number exceeds serial_max for this naip')
            WHERE (
                SELECT serial_max FROM naip WHERE id = NEW.naip_fk
            ) IS NOT NULL
            AND NEW.serial_number > (
                SELECT serial_max FROM naip WHERE id = NEW.naip_fk
            );
        END
    """)
    )
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_naip_serial_check_max_update
        BEFORE UPDATE ON naip_serial
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, 'serial_number exceeds serial_max for this naip')
            WHERE (
                SELECT serial_max FROM naip WHERE id = NEW.naip_fk
            ) IS NOT NULL
            AND NEW.serial_number > (
                SELECT serial_max FROM naip WHERE id = NEW.naip_fk
            );
        END
    """)
    )

    # trigger for set.updated_ts (set already had one from h2i3j4k5l6m7, but adding block_fk
    # doesn't invalidate it — the existing trigger still fires on any UPDATE to "set" rows)


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_naip_serial_check_max_update"))
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_naip_serial_check_max_insert"))

    op.drop_index("ix_banned_pair_global_unique", table_name="banned_pair")
    op.drop_index("ix_card_ban_global_unique", table_name="card_ban")

    with op.batch_alter_table("set") as batch_op:
        batch_op.drop_constraint("fk_set_block_fk", type_="foreignkey")
        batch_op.drop_column("block_fk")

    op.create_table(
        "naip_format",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("updated_ts", sa.String(), server_default=_TS_DEFAULT, nullable=True),
        sa.Column("naip_fk", sa.Integer(), sa.ForeignKey("naip.id"), nullable=False),
        sa.Column("format_fk", sa.Integer(), sa.ForeignKey("format.id"), nullable=False),
        sa.UniqueConstraint("naip_fk", "format_fk"),
    )
    op.create_index("ix_naip_format_naip_fk", "naip_format", ["naip_fk"])
    op.create_index("ix_naip_format_format_fk", "naip_format", ["format_fk"])
    op.execute(
        sa.text("""
        CREATE TRIGGER trg_naip_format_update
        AFTER UPDATE ON naip_format
        FOR EACH ROW
        WHEN NEW.updated_ts IS OLD.updated_ts
        BEGIN
            UPDATE naip_format SET updated_ts = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE id = NEW.id;
        END
    """)
    )
