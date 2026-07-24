from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentTextResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = await DocumentService(db).upload_document(current_user, file, title)
    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    sort: str = Query(default="created_at"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    items, total = DocumentService(db).list_documents(
        current_user, status_filter=status, query=q, page=page, limit=limit, sort=sort
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = DocumentService(db).get_document(document_id, current_user)
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/text", response_model=DocumentTextResponse)
def get_document_text(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentTextResponse:
    text = DocumentService(db).get_document_text(document_id, current_user)
    return DocumentTextResponse(
        document_id=text.document_id,
        extracted_text=text.extracted_text,
        page_count=text.page_count,
        extracted_at=text.extracted_at,
    )