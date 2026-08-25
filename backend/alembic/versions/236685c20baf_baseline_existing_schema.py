"""baseline existing schema

Revision ID: 236685c20baf
Revises:
Create Date: 2026-08-22 18:00:53.734356

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "236685c20baf"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
