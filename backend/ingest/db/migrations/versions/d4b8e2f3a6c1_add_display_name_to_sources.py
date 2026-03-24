"""add display_name to sources

Revision ID: d4b8e2f3a6c1
Revises: c3a7b9d1e5f2
Create Date: 2026-03-24 03:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d4b8e2f3a6c1"
down_revision = "c3a7b9d1e5f2"
branch_labels = None
depends_on = None


# Mapping of source name → display_name
DISPLAY_NAMES = {
    "azure-updates-rss": "Azure Updates",
    "azure-blog": "Azure Official Blog",
    "fabric-blog": "Fabric Blog",
    "github-blog": "GitHub Blog",
}


def upgrade() -> None:
    op.add_column("sources", sa.Column("display_name", sa.String(), nullable=True))

    # Set display_name for existing sources
    for name, display_name in DISPLAY_NAMES.items():
        op.execute(
            sa.text(
                "UPDATE sources SET display_name = :display_name WHERE name = :name"
            ).bindparams(display_name=display_name, name=name)
        )


def downgrade() -> None:
    op.drop_column("sources", "display_name")
