# app/services/dynamodb_service.py

import boto3

from boto3.dynamodb.conditions import Key

from app.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    DYNAMODB_TABLE_NAME,
)


dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

table = dynamodb.Table(
    DYNAMODB_TABLE_NAME
)


def get_table():

    return table


def save_metadata(item):

    table.put_item(
        Item=item
    )


def get_image(image_id):

    response = table.get_item(
        Key={
            "image_id": image_id
        }
    )

    return response.get("Item")


def delete_metadata(image_id):

    table.delete_item(
        Key={
            "image_id": image_id
        }
    )


def list_images(
    user_id=None,
    tag=None,
    limit=10,
    last_key=None
):

    query_params = {
        "Limit": limit
    }

    if last_key:

        query_params["ExclusiveStartKey"] = last_key

    if user_id:

        query_params["IndexName"] = "user_id-index"

        query_params["KeyConditionExpression"] = (
            Key("user_id").eq(user_id)
        )

        response = table.query(
            **query_params
        )

    else:

        response = table.scan(
            **query_params
        )

    items = response.get("Items", [])

    if tag:

        items = [
            item for item in items
            if tag in item.get("tags", [])
        ]

    return {
        "items": items,
        "last_evaluated_key": response.get(
            "LastEvaluatedKey"
        )
    }