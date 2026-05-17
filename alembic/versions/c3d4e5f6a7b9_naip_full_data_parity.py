"""naip full data parity with card

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-05-17
"""

from collections.abc import Sequence  # noqa: I001

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b9"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("PRAGMA foreign_keys = OFF"))

    # Add scalar columns to naip
    conn.execute(sa.text("ALTER TABLE naip ADD COLUMN cardtype_fk INTEGER REFERENCES card_type(id)"))
    conn.execute(sa.text("ALTER TABLE naip ADD COLUMN power INTEGER"))
    conn.execute(sa.text("ALTER TABLE naip ADD COLUMN life INTEGER"))
    conn.execute(sa.text("ALTER TABLE naip ADD COLUMN counter INTEGER"))
    conn.execute(sa.text("ALTER TABLE naip ADD COLUMN cost INTEGER"))

    # naip_color
    conn.execute(
        sa.text(
            """CREATE TABLE naip_color (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            color_fk   INTEGER NOT NULL REFERENCES color(id),
            UNIQUE (naip_fk, color_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_color_naip_fk ON naip_color (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_color_color_fk ON naip_color (color_fk)"))

    # naip_tribe
    conn.execute(
        sa.text(
            """CREATE TABLE naip_tribe (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            tribe_fk   INTEGER NOT NULL REFERENCES tribe(id),
            UNIQUE (naip_fk, tribe_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_tribe_naip_fk ON naip_tribe (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_tribe_tribe_fk ON naip_tribe (tribe_fk)"))

    # naip_attribute
    conn.execute(
        sa.text(
            """CREATE TABLE naip_attribute (
            id           INTEGER PRIMARY KEY,
            created_ts   TEXT,
            updated_ts   TEXT,
            naip_fk      INTEGER NOT NULL REFERENCES naip(id),
            attribute_fk INTEGER NOT NULL REFERENCES attribute(id),
            UNIQUE (naip_fk, attribute_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_attribute_naip_fk ON naip_attribute (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_attribute_attribute_fk ON naip_attribute (attribute_fk)"))

    # naip_keyword
    conn.execute(
        sa.text(
            """CREATE TABLE naip_keyword (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            keyword_fk INTEGER NOT NULL REFERENCES keyword(id),
            UNIQUE (naip_fk, keyword_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_keyword_naip_fk ON naip_keyword (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_keyword_keyword_fk ON naip_keyword (keyword_fk)"))

    # naip_resword
    conn.execute(
        sa.text(
            """CREATE TABLE naip_resword (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            resword_fk INTEGER NOT NULL REFERENCES resword(id),
            UNIQUE (naip_fk, resword_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_resword_naip_fk ON naip_resword (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_resword_resword_fk ON naip_resword (resword_fk)"))

    # naip_block
    conn.execute(
        sa.text(
            """CREATE TABLE naip_block (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            block_fk   INTEGER NOT NULL REFERENCES block(id),
            UNIQUE (naip_fk, block_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_block_naip_fk ON naip_block (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_block_block_fk ON naip_block (block_fk)"))

    # naip_format
    conn.execute(
        sa.text(
            """CREATE TABLE naip_format (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            naip_fk    INTEGER NOT NULL REFERENCES naip(id),
            format_fk  INTEGER NOT NULL REFERENCES format(id),
            UNIQUE (naip_fk, format_fk)
        )"""
        )
    )
    conn.execute(sa.text("CREATE INDEX ix_naip_format_naip_fk ON naip_format (naip_fk)"))
    conn.execute(sa.text("CREATE INDEX ix_naip_format_format_fk ON naip_format (format_fk)"))

    conn.execute(sa.text("PRAGMA foreign_keys = ON"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("PRAGMA foreign_keys = OFF"))

    for tbl in (
        "naip_format",
        "naip_block",
        "naip_resword",
        "naip_keyword",
        "naip_attribute",
        "naip_tribe",
        "naip_color",
    ):
        conn.execute(sa.text(f"DROP TABLE IF EXISTS {tbl}"))

    # Rebuild naip without the 5 new columns
    conn.execute(sa.text("ALTER TABLE naip RENAME TO naip_old"))
    conn.execute(
        sa.text(
            """CREATE TABLE naip (
            id         INTEGER PRIMARY KEY,
            created_ts TEXT,
            updated_ts TEXT,
            card_fk    INTEGER NOT NULL REFERENCES card(id),
            set_fk     INTEGER NOT NULL REFERENCES "set"(id),
            artist_fk  INTEGER REFERENCES artist(id),
            rarity_fk  INTEGER REFERENCES rarity(id),
            name_fk    INTEGER REFERENCES name(id),
            image_fk   INTEGER REFERENCES image(id),
            effect_fk  INTEGER REFERENCES effect(id),
            trigger_fk INTEGER REFERENCES trigger(id),
            is_default INTEGER NOT NULL DEFAULT 0,
            is_errata  INTEGER NOT NULL DEFAULT 0
        )"""
        )
    )
    conn.execute(
        sa.text(
            "INSERT INTO naip (id, created_ts, updated_ts, card_fk, set_fk, artist_fk, rarity_fk, "
            "name_fk, image_fk, effect_fk, trigger_fk, is_default, is_errata) "
            "SELECT id, created_ts, updated_ts, card_fk, set_fk, artist_fk, rarity_fk, "
            "name_fk, image_fk, effect_fk, trigger_fk, is_default, is_errata FROM naip_old"
        )
    )
    conn.execute(sa.text("CREATE UNIQUE INDEX ix_naip_one_default_per_card ON naip (card_fk) WHERE is_default = 1"))
    conn.execute(sa.text("DROP TABLE naip_old"))

    conn.execute(sa.text("PRAGMA foreign_keys = ON"))
