# app/services/s3_service.py

from typing import Optional

import boto3

from botocore.exceptions import ClientError

from app.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    SIGNED_URL_EXPIRATION,
)


s3_client = boto3.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def get_s3_client():

    return s3_client


def upload_file(key: str, body: bytes, content_type: Optional[str] = None):

    params = {
        "Bucket": S3_BUCKET_NAME,
        "Key": key,
        "Body": body,
    }

    if content_type:
        params["ContentType"] = content_type

    s3_client.put_object(**params)


def generate_download_url(key: str) -> str:

    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key
        },
        ExpiresIn=SIGNED_URL_EXPIRATION
    )


def delete_file(key: str):

    s3_client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=key
    )


def file_exists(key: str) -> bool:

    try:

        s3_client.head_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )

        return True

    except ClientError:

        return False