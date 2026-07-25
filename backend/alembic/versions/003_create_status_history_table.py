"""create status_history table

Revision ID: 003_create_status_history
Revises: 002_create_documents
Create Date: 2026-07-25 22:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_create_status_history"
down_revision: str | None = "002_create_documents"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

document_status = sa.Enum(
    "draft",
    "pending_review",
    "approved",
    "rejected",
    name="documentstatus",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "status_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("changed_by", sa.String(length=36), nullable=False),
        sa.Column("from_status", document_status, nullable=False),
        sa.Column("to_status", document_status, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_status_history_document_id"), "status_history", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_status_history_document_id"), table_name="status_history")
    op.drop_table("status_history")
