from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.document import Document, DocumentStatus, DocumentText


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
        owner_id: str,
        status: DocumentStatus | None = None,
        query: str | None = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
    ) -> tuple[list[Document], int]:
        q = self.db.query(Document).options(joinedload(Document.text_content))
        q = q.filter(Document.owner_id == owner_id)

        if status:
            q = q.filter(Document.status == status)

        if query:
            pattern = f"%{query}%"
            q = q.outerjoin(DocumentText).filter(
                or_(Document.title.ilike(pattern), DocumentText.extracted_text.ilike(pattern))
            )

        total = q.with_entities(func.count(Document.id.distinct())).scalar() or 0

        sort_column = Document.created_at.desc() if sort == "created_at" else Document.title.asc()
        items = q.order_by(sort_column).offset((page - 1) * limit).limit(limit).all()
        return items, total