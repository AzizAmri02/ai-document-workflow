def test_upload_pdf_creates_document(client, auth_headers, sample_pdf_bytes):
    response = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Sample Doc"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Sample Doc"
    assert body["status"] == "draft"


def test_upload_non_pdf_returns_422(client, auth_headers):
    response = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422


def test_user_cannot_access_other_users_document(client, auth_headers, sample_pdf_bytes, db_session):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]

    from app.models.user import User
    from app.utils.security import hash_password

    other = User(email="other@example.com", hashed_password=hash_password("password123"), full_name="Other")
    db_session.add(other)
    db_session.commit()

    login = client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/api/documents/{document_id}", headers=other_headers)
    assert response.status_code == 403


def test_search_and_filter_documents(client, auth_headers, sample_pdf_bytes):
    client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("invoice.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Invoice March"},
    )

    response = client.get("/api/documents?q=Invoice", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1