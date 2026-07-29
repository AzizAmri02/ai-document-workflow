from datetime import UTC, datetime, time

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_reviewer
from app.models.user import User
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentTextResponse,
    StatusHistoryResponse,
    StatusUpdateRequest,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


def _parse_upload_date(value: str, *, end_of_day: bool = False) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid date format, expected YYYY-MM-DD") from exc
    day_time = time(23, 59, 59, 999999) if end_of_day else time.min
    return datetime.combine(parsed, day_time, tzinfo=UTC)


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
    uploaded_from: str | None = Query(default=None),
    uploaded_to: str | None = Query(default=None),
    sort: str = Query(default="created_at"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    from_date = _parse_upload_date(uploaded_from) if uploaded_from else None
    to_date = _parse_upload_date(uploaded_to, end_of_day=True) if uploaded_to else None
    items, total = DocumentService(db).list_documents(
        current_user,
        status_filter=status,
        query=q,
        uploaded_from=from_date,
        uploaded_to=to_date,
        page=page,
        limit=limit,
        sort=sort,
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/review-queue", response_model=DocumentListResponse)
def review_queue(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_reviewer),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    items, total = DocumentService(db).list_documents(current_user, page=page, limit=limit, review_queue=True)
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


@router.patch("/{document_id}/status", response_model=DocumentResponse)
def update_status(
    document_id: str,
    payload: StatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = DocumentService(db).update_status(document_id, current_user, payload.status, payload.comment)
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/history", response_model=list[StatusHistoryResponse])
def get_status_history(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StatusHistoryResponse]:
    history = DocumentService(db).get_status_history(document_id, current_user)
    return [StatusHistoryResponse.model_validate(item) for item in history]
