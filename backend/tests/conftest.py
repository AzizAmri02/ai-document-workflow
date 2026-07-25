import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from pypdf import PdfWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import UserRole
from app.utils.security import hash_password


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@pytest.fixture()
def auth_headers(client, db_session):
    from app.models.user import User

    user = User(
        email="user@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role=UserRole.user,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def reviewer_headers(client, db_session):
    from app.models.user import User

    reviewer = User(
        email="reviewer@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test Reviewer",
        role=UserRole.reviewer,
    )
    db_session.add(reviewer)
    db_session.commit()

    response = client.post("/api/auth/login", json={"email": "reviewer@example.com", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
