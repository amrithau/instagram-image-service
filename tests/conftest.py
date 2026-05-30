# tests/conftest.py

import pytest
from botocore.exceptions import ClientError

from app.aws_setup import _client, ensure_localstack_resources
from app.constants import DYNAMODB_TABLE_NAME, S3_BUCKET_NAME


def _clear_s3_bucket():
    s3 = _client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=S3_BUCKET_NAME):
        contents = page.get("Contents", [])

        if not contents:
            continue

        s3.delete_objects(
            Bucket=S3_BUCKET_NAME,
            Delete={
                "Objects": [
                    {"Key": obj["Key"]}
                    for obj in contents
                ]
            },
        )


def _clear_dynamodb_table():
    dynamodb = _client("dynamodb")
    paginator = dynamodb.get_paginator("scan")

    for page in paginator.paginate(TableName=DYNAMODB_TABLE_NAME):
        items = page.get("Items", [])

        for item in items:
            dynamodb.delete_item(
                TableName=DYNAMODB_TABLE_NAME,
                Key={"image_id": item["image_id"]},
            )


@pytest.fixture(scope="session", autouse=True)
def localstack_resources():
    ensure_localstack_resources()


@pytest.fixture(autouse=True)
def reset_storage(localstack_resources):
    _clear_s3_bucket()
    _clear_dynamodb_table()
    yield
    _clear_s3_bucket()
    _clear_dynamodb_table()
