def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password123", "full_name": "New User"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dup@example.com", "password": "password123", "full_name": "Dup User"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login_invalid_password_returns_401(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "password123", "full_name": "Login User"},
    )
    response = client.post("/api/auth/login", json={"email": "login@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_protected_route_without_token_returns_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
