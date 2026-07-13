"""Routers for posts feed, like and upload."""

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import Like, Post, User, db
from services.storage import get_file_url, upload_to_seaweed

feed_bp = Blueprint("feed", __name__)


def _get_valid_user_id():
    """Return the session's user_id only if that user still exists in the database."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return None
    return user_id


@feed_bp.route("/")
def show_feed():
    """Show feed."""
    user_id = _get_valid_user_id()
    unlocked_posts = session.get("unlocked_posts", [])

    posts = Post.query.order_by(Post.created_at.asc()).all()
    birds_data = []
    for post in posts:
        likes_count = post.likes.count()
        is_liked = False
        if user_id:
            is_liked = (
                Like.query.filter_by(user_id=user_id, post_id=post.id).first()
                is not None
            )

        has_password = bool(post.password) and post.id not in unlocked_posts
        if has_password:
            file_url = ""
            location = ""
        else:
            file_url = get_file_url(post.image_filename)
            location = post.location

        birds_data.append(
            {
                "id": post.id,
                "name": post.title,
                "desc": post.description,
                "loc": location,
                "img": file_url,
                "likes_count": likes_count,
                "is_liked": is_liked,
                "has_password": has_password,
            }
        )

    if not birds_data:
        birds_data = [
            {
                "id": 0,
                "name": "No posts yet",
                "desc": "Sign in and upload",
                "loc": "Nowhere",
                "img": "",
                "likes_count": 0,
                "is_liked": False,
                "has_password": False,
            }
        ]
    return render_template(
        "feed.html",
        birds_data=birds_data,
        username=session.get("username"),
        logged_in=bool(user_id),
    )


@feed_bp.route("/like/<int:post_id>", methods=["POST"])
def toggle_like(post_id):
    """Like."""
    user_id = _get_valid_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    post = Post.query.get_or_404(post_id)
    unlocked_posts = session.get("unlocked_posts", [])
    if post.password and post.id not in unlocked_posts:
        return jsonify({"error": "Post is locked"}), 403

    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        action = "unliked"
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        action = "liked"

    likes_count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({"action": action, "likes_count": likes_count})


@feed_bp.route("/upload", methods=["POST"])
def upload():
    """New posts."""
    user_id = _get_valid_user_id()
    if not user_id:
        return redirect(url_for("auth.index"))

    file = request.files.get("photo")
    object_key = None
    if file and file.filename != "":
        file.stream.seek(0)
        object_key = upload_to_seaweed(file.stream, file.filename)

    if not object_key:
        return "Upload failed: could not save the image file.", 500

    password_input = request.form.get("password")
    post_password = (
        password_input.strip() if password_input and password_input.strip() else None
    )
    hash_pw = generate_password_hash(post_password) if post_password else None

    new_post = Post(
        title=request.form.get("title"),
        location=request.form.get("location"),
        description=request.form.get("description"),
        image_filename=object_key,
        user_id=user_id,
        password=hash_pw,
    )
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for("feed.show_feed"))


@feed_bp.route("/unlock/<int:post_id>", methods=["POST"])
def unlock(post_id):
    """Unlock post."""
    post = Post.query.get_or_404(post_id)

    password_input = request.form.get("password")
    if not post.password or check_password_hash(post.password, password_input):
        unlocked_posts = session.get("unlocked_posts", [])
        if post.id not in unlocked_posts:
            unlocked_posts.append(post.id)
            session["unlocked_posts"] = unlocked_posts
        file_url = get_file_url(post.image_filename)
        return jsonify({"success": True, "img": file_url, "loc": post.location}), 200

    return jsonify({"error": "Incorrect password"}), 401