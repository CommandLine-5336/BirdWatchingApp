"""Script that boots the Flask application."""

import os

from dotenv import load_dotenv
from flask import Flask

from models import db
from routes.auth import auth_bp
from routes.feed import feed_bp

load_dotenv()


def create_app():
    """Application factory establishing databases, configurations, and blueprints."""
    application = Flask(__name__)
    application.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_dev_key")

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    application.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    application.config["UPLOAD_FOLDER"] = os.path.join(
        application.root_path, "static/images"
    )
    os.makedirs(application.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(application)

    application.register_blueprint(auth_bp)
    application.register_blueprint(feed_bp)

    with application.app_context():
        db.create_all()

    return application


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4242, debug=True)
