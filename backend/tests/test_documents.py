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


def test_search_by_filename(client, auth_headers, sample_pdf_bytes):
    client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("quarterly-report.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Q1 Summary"},
    )

    response = client.get("/api/documents?q=quarterly-report", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_search_by_extracted_text(client, auth_headers, sample_pdf_bytes, db_session):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("notes.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Meeting Notes"},
    )
    document_id = upload.json()["id"]

    from app.models.document import DocumentText

    text_row = db_session.query(DocumentText).filter(DocumentText.document_id == document_id).one()
    text_row.extracted_text = "Contains the keyword retention analysis"
    db_session.commit()

    response = client.get("/api/documents?q=retention", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_filter_by_status(client, auth_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("draft.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]
    client.patch(
        f"/api/documents/{document_id}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    draft_response = client.get("/api/documents?status=draft", headers=auth_headers)
    pending_response = client.get("/api/documents?status=pending_review", headers=auth_headers)

    assert draft_response.status_code == 200
    assert pending_response.status_code == 200
    assert all(item["status"] == "draft" for item in draft_response.json()["items"])
    assert any(item["id"] == document_id for item in pending_response.json()["items"])


def test_filter_by_upload_date(client, auth_headers, sample_pdf_bytes, db_session):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("dated.pdf", sample_pdf_bytes, "application/pdf")},
    )
    document_id = upload.json()["id"]

    from datetime import UTC, datetime

    from app.models.document import Document

    document = db_session.query(Document).filter(Document.id == document_id).one()
    document.created_at = datetime(2026, 3, 15, 12, 0, tzinfo=UTC)
    db_session.commit()

    in_range = client.get("/api/documents?uploaded_from=2026-03-01&uploaded_to=2026-03-31", headers=auth_headers)
    out_of_range = client.get("/api/documents?uploaded_from=2026-04-01&uploaded_to=2026-04-30", headers=auth_headers)

    assert in_range.status_code == 200
    assert out_of_range.status_code == 200
    assert in_range.json()["total"] == 1
    assert out_of_range.json()["total"] == 0


def test_pagination_returns_expected_page(client, auth_headers, sample_pdf_bytes):
    for index in range(3):
        client.post(
            "/api/documents/upload",
            headers=auth_headers,
            files={"file": (f"doc-{index}.pdf", sample_pdf_bytes, "application/pdf")},
            data={"title": f"Document {index}"},
        )

    page_one = client.get("/api/documents?limit=2&page=1", headers=auth_headers)
    page_two = client.get("/api/documents?limit=2&page=2", headers=auth_headers)

    assert page_one.status_code == 200
    assert page_two.status_code == 200
    assert page_one.json()["total"] == 3
    assert len(page_one.json()["items"]) == 2
    assert len(page_two.json()["items"]) == 1


def test_sort_by_upload_date(client, auth_headers, sample_pdf_bytes, db_session):
    first = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("first.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "First"},
    ).json()["id"]
    second = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("second.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Second"},
    ).json()["id"]

    from datetime import UTC, datetime

    from app.models.document import Document

    first_doc = db_session.query(Document).filter(Document.id == first).one()
    second_doc = db_session.query(Document).filter(Document.id == second).one()
    first_doc.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    second_doc.created_at = datetime(2026, 2, 1, tzinfo=UTC)
    db_session.commit()

    newest = client.get("/api/documents?sort=created_at", headers=auth_headers)
    oldest = client.get("/api/documents?sort=created_at_asc", headers=auth_headers)

    assert newest.json()["items"][0]["id"] == second
    assert oldest.json()["items"][0]["id"] == first


def test_user_list_excludes_other_users_documents(client, auth_headers, sample_pdf_bytes, db_session):
    client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("private.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Private Budget"},
    )

    from app.models.user import User
    from app.utils.security import hash_password

    other = User(email="other@example.com", hashed_password=hash_password("password123"), full_name="Other")
    db_session.add(other)
    db_session.commit()

    login = client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/api/documents?q=Private", headers=other_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_reviewer_list_includes_pending_not_other_drafts(
    client, auth_headers, reviewer_headers, sample_pdf_bytes
):
    draft = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("owner-draft.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Owner Draft Only"},
    ).json()["id"]
    pending = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("owner-pending.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "Owner Pending Review"},
    ).json()["id"]
    client.patch(
        f"/api/documents/{pending}/status",
        headers=auth_headers,
        json={"status": "pending_review"},
    )

    response = client.get("/api/documents", headers=reviewer_headers)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert pending in ids
    assert draft not in ids


def test_invalid_sort_returns_422(client, auth_headers):
    response = client.get("/api/documents?sort=title", headers=auth_headers)
    assert response.status_code == 422


def test_invalid_upload_date_returns_422(client, auth_headers):
    response = client.get("/api/documents?uploaded_from=2026-13-40", headers=auth_headers)
    assert response.status_code == 422


def test_search_wildcard_characters_are_literal(client, auth_headers, sample_pdf_bytes, db_session):
    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("percent.pdf", sample_pdf_bytes, "application/pdf")},
        data={"title": "100% complete"},
    )
    document_id = upload.json()["id"]

    from app.models.document import Document

    document = db_session.query(Document).filter(Document.id == document_id).one()
    document.title = "100% complete"
    db_session.commit()

    response = client.get("/api/documents?q=100%25", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


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
