"""Create a reviewer account for local development."""

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password


def main() -> None:
    db = SessionLocal()
    email = "reviewer@example.com"
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"Reviewer already exists: {email}")
        return

    reviewer = User(
        email=email,
        hashed_password=hash_password("password123"),
        full_name="Default Reviewer",
        role=UserRole.reviewer,
    )
    db.add(reviewer)
    db.commit()
    print(f"Created reviewer: {email} / password123")


if __name__ == "__main__":
    main()
