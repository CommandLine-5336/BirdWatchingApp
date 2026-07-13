"""Module handling interactions with local images storage."""

import os
import uuid

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from flask import current_app, url_for

load_dotenv()

def get_s3_client():
    """Initialize and return a configured boto3 S3 client connection."""
    return boto3.client(
        "s3",
        region_name=os.getenv("S3_REGION"),
        # endpoint_url=os.getenv("S3_ENDPOINT"),
        # aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        # aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
        use_ssl=False,
    )


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
