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


def test_valid_status_transition_pending_to_approved(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]

    submit = client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )
    assert submit.status_code == 200

    approve = client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "approved"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"


def test_invalid_transition_draft_to_approved_returns_400(client, auth_headers, reviewer_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "approved"},
    )
    assert response.status_code == 400


def test_reject_requires_reviewer_role(client, auth_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(f"/api/documents/{document_id}/status", headers=auth_headers, json={"status": "pending_review"})

    response = client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "rejected", "comment": "Needs changes"},
    )
    assert response.status_code == 403


def test_status_history_recorded_on_transition(client, auth_headers, reviewer_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(f"/api/documents/{document_id}/status", headers=auth_headers, json={"status": "pending_review"})
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "rejected", "comment": "Missing signature"},
    )

    history = client.get(f"/api/documents/{document_id}/history", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()) >= 2


def test_review_queue_requires_reviewer_role(client, auth_headers, sample_pdf_bytes):
    client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )

    response = client.get("/api/documents/review-queue", headers=auth_headers)
    assert response.status_code == 403


def test_review_queue_returns_only_pending_documents(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    response = client.get("/api/documents/review-queue", headers=reviewer_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all(item["status"] == "pending_review" for item in body["items"])


def test_reject_without_comment_returns_422(client, auth_headers, reviewer_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    response = client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "rejected"},
    )
    assert response.status_code == 422


def test_owner_cannot_approve_document(client, auth_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    response = client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "approved"},
    )
    assert response.status_code == 403


def test_reviewer_cannot_submit_other_users_document(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "pending_review"},
    )
    assert response.status_code == 403


def test_rejected_document_can_be_resubmitted(client, auth_headers, reviewer_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "rejected", "comment": "Needs revision"},
    )

    resubmit = client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )
    assert resubmit.status_code == 200
    assert resubmit.json()["status"] == "pending_review"


def test_reviewer_can_access_other_users_pending_document(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    response = client.get(f"/api/documents/{document_id}", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "pending_review"


def test_status_history_records_transition_details(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=reviewer_headers,
        json={"status": "rejected", "comment": "Missing appendix"},
    )

    history = client.get(f"/api/documents/{document_id}/history", headers=auth_headers)
    assert history.status_code == 200
    entries = history.json()
    rejection = next(entry for entry in entries if entry["to_status"] == "rejected")
    assert rejection["from_status"] == "pending_review"
    assert rejection["comment"] == "Missing appendix"
