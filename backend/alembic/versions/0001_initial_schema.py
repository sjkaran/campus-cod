"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-28

NOTE: this bootstrap revision builds the schema from the current SQLAlchemy models so the
project runs end-to-end immediately. Before the first production deployment, regenerate it
as explicit DDL (see README > "Freezing the initial migration"). Every later change should
be a normal `alembic revision --autogenerate`.
"""
from alembic import op

from app.database.base import Base
import app.models  # noqa: F401

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
