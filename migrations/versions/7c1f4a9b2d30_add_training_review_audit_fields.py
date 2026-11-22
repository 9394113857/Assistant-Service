"""add human reviewer audit fields

Revision ID: 7c1f4a9b2d30
Revises: 13518dd95fc3
Create Date: 2026-11-22
"""
from alembic import op
import sqlalchemy as sa


revision = "7c1f4a9b2d30"
down_revision = "13518dd95fc3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("assistant_training_logs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reviewer_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("assistant_training_logs", schema=None) as batch_op:
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("reviewer_user_id")
