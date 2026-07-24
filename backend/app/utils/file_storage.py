from pathlib import Path
import re
import uuid

from fastapi import HTTPException, UploadFile, status

from app.config import settings

PDF_MAGIC = b"%PDF"


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    safe = re.sub(r"[^\w.\-]", "_", name)
    return safe[:200] if safe else "document.pdf"


def validate_pdf_upload(file: UploadFile, content: bytes) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only PDF files are allowed")

    if file.content_type and file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid PDF content type")

    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is empty")

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_bytes} bytes",
        )

    if not content.startswith(PDF_MAGIC):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is not a valid PDF")


def _ensure_within_root(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid storage path")
    return resolved


async def save_upload_file(user_id: str, document_id: str, file: UploadFile, content: bytes) -> str:
    upload_root = Path(settings.upload_dir).resolve()
    user_dir = _ensure_within_root(upload_root / user_id, upload_root)
    user_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "document.pdf")
    stored_name = f"{document_id}_{safe_name}"
    destination = _ensure_within_root(user_dir / stored_name, upload_root)
    destination.write_bytes(content)

    return str(destination.relative_to(upload_root)).replace("\\", "/")
