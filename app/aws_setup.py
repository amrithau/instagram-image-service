# app/aws_setup.py

import boto3
from botocore.exceptions import ClientError

from app.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    DYNAMODB_TABLE_NAME,
    S3_BUCKET_NAME,
)


def _client(service: str):
    return boto3.client(
        service,
        region_name=AWS_REGION,
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def ensure_s3_bucket() -> None:
    s3 = _client("s3")

    try:
        s3.head_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=S3_BUCKET_NAME)


def ensure_dynamodb_table() -> None:
    dynamodb = _client("dynamodb")

    try:
        dynamodb.describe_table(TableName=DYNAMODB_TABLE_NAME)
        return
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    dynamodb.create_table(
        TableName=DYNAMODB_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "image_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "image_id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "user_id-index",
                "KeySchema": [
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=DYNAMODB_TABLE_NAME)


def ensure_localstack_resources() -> None:
    ensure_s3_bucket()
    ensure_dynamodb_table()
