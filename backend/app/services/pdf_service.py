from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(content: bytes) -> tuple[str, int]:
    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages).strip(), len(reader.pages)
