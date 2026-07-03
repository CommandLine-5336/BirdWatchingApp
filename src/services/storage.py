import boto3
import os
import uuid
import botocore
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
        config=Config(
            s3={'addressing_style': 'path'},
            signature_version='s3v4'
        ),
        use_ssl=False
    )

def upload_to_seaweed(file_stream, filename):
    s3 = get_s3_client()
    bucket = os.getenv('S3_BUCKET')

    ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
    object_key = f"uploads/{uuid.uuid4().hex}.{ext}"

    try:
        s3.upload_fileobj(file_stream, bucket, object_key)
        return object_key
    except ClientError as e:
        print(f"S3 Uplod Error: {e}")
        return None

def get_file_url(filename):
    if not filename:
        return ""
    s3 = get_s3_client()
    try:
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': os.getenv('S3_BUCKET'), 'Key': filename},
            ExpiresIn=3600
        )
    except ClientError as e:
        print(f"Presigned URL Error: {e}")
        return ""
    #