import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.document import DocumentStatus


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    changed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    from_status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False)
    to_status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    document = relationship("Document", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")
