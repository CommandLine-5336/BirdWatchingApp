"""Blueprint router containing registration and authentication functions."""

from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def index():
    """Redirect to logins and registrations."""
    error = None
    if request.method == "GET":
        session.clear()
        return render_template("auth.html", error=error)

    form_username = request.form.get("username")
    password = request.form.get("password")
    action = request.form.get("action")

    if not form_username or not password:
        return render_template("auth.html", error="Both fields are required!")

    if action == "register":
        return _handle_registration(form_username, password)

    if action == "login":
        return _handle_login(form_username, password)

    return render_template("auth.html", error=error)


def _handle_registration(form_username, password):
    """Registration."""
    existing_user = User.query.filter_by(login=form_username).first()
    if not existing_user:
        hash_pw = generate_password_hash(password)
        new_user = User(login=form_username, password=hash_pw)
        db.session.add(new_user)
        db.session.commit()

        session.clear()
        session["user_id"] = new_user.id
        session["username"] = new_user.login
        return redirect(url_for("feed.show_feed"))
    return render_template("auth.html", error="Username already taken!")


def _handle_login(form_username, password):
    """Login."""
    user = User.query.filter_by(login=form_username).first()
    if user and check_password_hash(user.password, password):
        session.clear()
        session["user_id"] = user.id
        session["username"] = user.login
        return redirect(url_for("feed.show_feed"))
    return render_template("auth.html", error="Invalid username or password")


@auth_bp.route("/logout")
def logout():
    """Logout."""
    session.clear()
    return redirect(url_for("auth.index"))
