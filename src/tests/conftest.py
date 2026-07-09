"""Module for testing BirdWatchingApp."""

# pylint: disable=redefined-outer-name, wrong-import-position

import os
import sys

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app import create_app
from models import db, User


@pytest.fixture
def test_app():
    """Configures the app for testing."""
    os.environ["TEST_DB_URI"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test_secret"

    flask_app = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(test_app):
    """Returns test client HTTP."""
    return test_app.test_client()


@pytest.fixture
def db_session(test_app):
    """Provides session DB for tests."""
    with test_app.app_context():
        yield db.session


@pytest.fixture
def test_user(db_session):
    """Creates basic user."""
    user = User(
        login="ana",
        password=generate_password_hash("securepass", method="pbkdf2:sha256"),
    )
    db_session.add(user)
    db_session.commit()
    return user
