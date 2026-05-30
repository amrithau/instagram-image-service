# app/constants.py

AWS_REGION = "us-east-1"

AWS_ENDPOINT_URL = "http://localhost:4566"

S3_BUCKET_NAME = "images-bucket"

DYNAMODB_TABLE_NAME = "images"

SIGNED_URL_EXPIRATION = 3600

# LocalStack accepts any credentials; pass explicitly so tests and the API
# work without setting AWS_* environment variables.
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"
