"""add naip_serial updated_ts trigger

Revision ID: 75adbb637f38
Revises: d67a59a0943a
Create Date: 2026-05-20 13:35:19.000104

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "75adbb637f38"
down_revision: str | Sequence[str] | None = "d67a59a0943a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("""
        CREATE TRIGGER trg_naip_serial_update
        AFTER UPDATE ON naip_serial
        FOR EACH ROW
        WHEN NEW.updated_ts IS OLD.updated_ts
        BEGIN
            UPDATE naip_serial
            SET updated_ts = strftime('%Y-%m-%d %H:%M:%f', 'now')
            WHERE id = NEW.id;
        END
    """))


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_naip_serial_update"))
