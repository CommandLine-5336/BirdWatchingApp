"""Tests for authentication routes."""

from models import User


def test_login_page_loads(client):
    """Verify that the login page loads."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"BirdTok" in response.data


def test_auth_empty_fields(client):
    """Test login with empty credentials."""
    response = client.post(
        "/login", data={"action": "login", "username": "", "password": ""}
    )
    assert b"Both fields are required!" in response.data


def test_register_new_user(client, db_session):
    """Test successful user registration."""
    new_username = "new_random_user"
    response = client.post(
        "/login",
        data={
            "action": "register",
            "username": new_username,
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/"

    user = db_session.query(User).filter_by(login=new_username).first()
    assert user is not None


def test_register_duplicate_user(client, test_user):
    """Test registration with existing username."""
    response = client.post(
        "/login",
        data={
            "action": "register",
            "username": test_user.login,
            "password": "some_new_password",
        },
    )
    assert b"Username already taken!" in response.data


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/login",
        data={"action": "login", "username": test_user.login, "password": "securepass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/"


def test_login_invalid_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "login",
        data={
            "action": "login",
            "username": test_user.login,
            "password": "wrong_password",
        },
    )
    assert b"Invalid username or password." in response.data


def test_logout(client, test_user):
    """Test logout functionality."""
    with client.session_transaction() as session:
        session["user_id"] = test_user.id
        session["username"] = test_user.login

    response = client.get("/logout", follow_redirects=True)
    assert response.request.path == "/login"
