from app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_blank_pdf(sample_pdf_bytes):
    text, page_count = extract_text_from_pdf(sample_pdf_bytes)
    assert page_count == 1
    assert isinstance(text, str)
