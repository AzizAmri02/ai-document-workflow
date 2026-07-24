import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.pdf_service import extract_text_from_pdf
from app.utils.file_storage import save_upload_file, validate_pdf_upload


class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)

    def _ensure_access(self, document: Document, user: User) -> None:
        if document.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def upload_document(self, user: User, file: UploadFile, title: str | None = None) -> Document:
        content = await file.read()
        validate_pdf_upload(file, content)

        document_id = str(uuid.uuid4())
        file_path = await save_upload_file(user.id, document_id, file, content)
        extracted_text, page_count = extract_text_from_pdf(content)
        display_title = title or (file.filename or "Untitled document")

        return self.repo.create(
            document_id=document_id,
            owner_id=user.id,
            title=display_title,
            filename=file.filename or "document.pdf",
            file_path=file_path,
            file_size_bytes=len(content),
            extracted_text=extracted_text,
            page_count=page_count,
        )

    def get_document(self, document_id: str, user: User) -> Document:
        document = self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        self._ensure_access(document, user)
        return document

    def get_document_text(self, document_id: str, user: User):
        document = self.get_document(document_id, user)
        if not document.text_content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extracted text not found")
        return document.text_content

    def list_documents(
        self,
        user: User,
        *,
        status_filter: str | None = None,
        query: str | None = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
    ) -> tuple[list[Document], int]:
        status_enum = None
        if status_filter:
            try:
                status_enum = DocumentStatus(status_filter)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status") from exc

        return self.repo.list_documents(
            owner_id=user.id,
            status=status_enum,
            query=query,
            page=page,
            limit=limit,
            sort=sort,
        )