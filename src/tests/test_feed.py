"""Tests for post feed and uploads."""

import io
from unittest import mock
from werkzeug.security import generate_password_hash
from models import Post


def test_feed_empty(client):
    """Check empty feed message."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"No posts yet" in response.data


def test_upload_unauthorized(client):
    """Check restricted access to upload."""
    response = client.post("/upload", follow_redirects=True)
    assert response.request.path == "/login"


@mock.patch("routes.feed.get_file_url", return_value="http://mock-s3/img.jpg")
@mock.patch("routes.feed.upload_to_seaweed", return_value="uploads/mock_img.jpg")
def test_upload_post(mock_upload, _mock_get, client, db_session, test_user):
    """Test successful post upload."""
    with client.session_transaction() as session:
        session["user_id"] = test_user.id

    data = {
        "photo": (io.BytesIO(b"fake image data"), "bird.jpg"),
        "title": "Barn Owl",
        "location": "Lviv",
        "description": "Spotted on the roof",
    }

    response = client.post(
        "/upload", data=data, content_type="multipart/form-data", follow_redirects=True
    )

    assert response.status_code == 200
    mock_upload.assert_called_once()

    post = db_session.query(Post).filter_by(user_id=test_user.id).first()
    assert post.title == "Barn Owl"
    assert post.password is None


def test_like_unauthorized(client, db_session, test_user):
    """Test like functionality without auth."""
    post = Post(title="Test Post", image_filename="img.jpg", user_id=test_user.id)
    db_session.app(post)
    db_session.flush()
    response = client.post(f"/like/{post.id}")
    assert response.status_code == 401
    assert response.json["error"] == "Unathorized"


def test_toggle_like(client, db_session, test_user):
    """Test like and unlike actions."""
    post = Post(title="Test Post", image_filename="img.img", user_id=test_user.id)
    db_session.add(post)
    db_session.flush()
    post_id = post.id

    with client.session_transaction() as session:
        session["user.id"] = test_user.id

        response = client.post(f"/like/{post_id}")
        assert response.status_code == 200
        assert response.json["action"] == "liked"
        assert response.json["likes_count"] == 1

        response2 = client.post(f"/like/{post_id}")
        assert response2.json["action"] == "unliked"
        assert response2.json["likes_count"] == 0


@mock.patch("routes.feed.get_file_url", return_value="http://mock-s3/img.jpg")
def test_unlocking_post(_mock_get, client, db_session, test_user):
    """Test upload with valid password."""
    post = Post(
        title="Locked Post",
        image_filename="secret.jpg",
        password=generate_password_hash("correct_pass", method="pbkdf2:sha256"),
        user_id=test_user.id,
    )
    db_session.add(post)
    db_session.flush()
    post_id = post.id

    response_fail = client.post(f"/unlock/{post_id}", data={"password": "wrong"})
    assert response_fail.status_code == 401
    assert response_fail.json["error"] == "Incorrect password"

    response_success = client.post(
        f"/unlock/{post_id}", data={"password": "correct_password"}
    )
    assert response_success.status_code == 200
    assert response_success.json["success"] is True
    assert response_success.json["error"] == "Incorrect password"
