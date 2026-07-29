from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.document import Document, DocumentStatus, DocumentText
from app.models.status_history import StatusHistory
from app.models.user import User


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_id: str,
        owner_id: str,
        title: str,
        filename: str,
        file_path: str,
        file_size_bytes: int,
        extracted_text: str,
        page_count: int,
    ) -> Document:
        document = Document(
            id=document_id,
            owner_id=owner_id,
            title=title,
            filename=filename,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.draft,
        )
        self.db.add(document)
        self.db.flush()

        text_row = DocumentText(
            document_id=document.id,
            extracted_text=extracted_text,
            page_count=page_count,
        )
        self.db.add(text_row)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: str) -> Document | None:
        return (
            self.db.query(Document)
            .options(joinedload(Document.text_content))
            .filter(Document.id == document_id)
            .first()
        )

    def get_text(self, document_id: str) -> DocumentText | None:
        return self.db.query(DocumentText).filter(DocumentText.document_id == document_id).first()

    def list_documents(
        self,
        *,
        owner_id: str | None = None,
        reviewer: bool = False,
        reviewer_user_id: str | None = None,
        status: DocumentStatus | None = None,
        query: str | None = None,
        uploaded_from: datetime | None = None,
        uploaded_to: datetime | None = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
    ) -> tuple[list[Document], int]:
        q = self.db.query(Document).options(joinedload(Document.text_content))

        if reviewer:
            q = q.filter(Document.status == DocumentStatus.pending_review)
        elif reviewer_user_id:
            q = q.filter(
                or_(
                    Document.owner_id == reviewer_user_id,
                    Document.status == DocumentStatus.pending_review,
                )
            )
        elif owner_id:
            q = q.filter(Document.owner_id == owner_id)

        if status:
            q = q.filter(Document.status == status)

        if uploaded_from:
            q = q.filter(Document.created_at >= uploaded_from)
        if uploaded_to:
            q = q.filter(Document.created_at <= uploaded_to)

        if query:
            pattern = f"%{_escape_like(query.strip())}%"
            q = q.outerjoin(DocumentText).filter(
                or_(
                    Document.title.ilike(pattern, escape="\\"),
                    Document.filename.ilike(pattern, escape="\\"),
                    DocumentText.extracted_text.ilike(pattern, escape="\\"),
                )
            )

        total = q.with_entities(func.count(Document.id.distinct())).scalar() or 0

        if sort == "created_at_asc":
            sort_column = Document.created_at.asc()
        else:
            sort_column = Document.created_at.desc()

        items = q.distinct().order_by(sort_column).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def update_status(
        self,
        document: Document,
        new_status: DocumentStatus,
        changed_by: User,
        comment: str | None,
    ) -> StatusHistory:
        history = StatusHistory(
            document_id=document.id,
            changed_by=changed_by.id,
            from_status=document.status,
            to_status=new_status,
            comment=comment,
        )
        document.status = new_status
        self.db.add(history)
        self.db.commit()
        self.db.refresh(document)
        self.db.refresh(history)
        return history

    def list_status_history(self, document_id: str) -> list[StatusHistory]:
        return (
            self.db.query(StatusHistory)
            .filter(StatusHistory.document_id == document_id)
            .order_by(StatusHistory.created_at.desc())
            .all()
        )
