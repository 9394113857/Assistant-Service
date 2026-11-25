"""add guest token hash to chat sessions

Revision ID: 7c2f91a4d6b8
Revises: 4246655a1fae
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c2f91a4d6b8"
down_revision = "13518dd95fc3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "chat_sessions",
        sa.Column("guest_token_hash", sa.String(length=64), nullable=True),
    )
    op.create_unique_constraint(
        "uq_chat_sessions_guest_token_hash",
        "chat_sessions",
        ["guest_token_hash"],
    )


def downgrade():
    op.drop_constraint(
        "uq_chat_sessions_guest_token_hash",
        "chat_sessions",
        type_="unique",
    )
    op.drop_column("chat_sessions", "guest_token_hash")
