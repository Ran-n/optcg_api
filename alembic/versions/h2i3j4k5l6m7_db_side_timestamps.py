#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/05/18 00:00:00.000000
Revised: 2026/05/18 13:45:51.261930

add db-side timestamp defaults and update triggers

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-05-18
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "h2i3j4k5l6m7"
down_revision: str | Sequence[str] | None = "g1h2i3j4k5l6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES = [
    "set_type",
    "card_type",
    "artist",
    "rarity",
    "tribe",
    "attribute",
    "color",
    "block",
    "format",
    "keyword",
    "resword",
    "set",
    "name",
    "image",
    "effect",
    "trigger",
    "card",
    "naip",
    "card_effect_history",
    "card_trigger_history",
    "card_tribe",
    "card_attribute",
    "card_color",
    "card_rarity",
    "card_block",
    "card_format",
    "card_keyword",
    "card_resword",
    "naip_color",
    "naip_tribe",
    "naip_attribute",
    "naip_keyword",
    "naip_resword",
    "naip_block",
    "naip_format",
]

_TS_EXPR = "strftime('%Y-%m-%d %H:%M:%f', 'now')"


def upgrade() -> None:
    for tbl in _TABLES:
        op.execute(
            sa.text(f"""
                CREATE TRIGGER IF NOT EXISTS trg_{tbl}_update
                AFTER UPDATE ON "{tbl}"
                FOR EACH ROW
                WHEN NEW.updated_ts IS OLD.updated_ts
                BEGIN
                    UPDATE "{tbl}"
                    SET updated_ts = {_TS_EXPR}
                    WHERE id = NEW.id;
                END
            """)
        )


def downgrade() -> None:
    for tbl in _TABLES:
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS trg_{tbl}_update"))
