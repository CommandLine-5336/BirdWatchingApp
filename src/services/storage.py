"""Module handling interactions with local images storage."""

import os
import uuid

from flask import current_app, url_for


def upload_to_seaweed(file_stream, filename):
    """Save an uploaded file to the local uploads folder and return its stored name."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, unique_name)

    try:
        with open(file_path, "wb") as f:
            f.write(file_stream.read())
        return unique_name
    except OSError as e:
        print(f"Local upload error: {e}")
        return None


def get_file_url(filename):
    """Build a URL pointing to a locally stored image file."""
    if not filename:
        return ""
    return url_for("static", filename=f"images/{filename}")
