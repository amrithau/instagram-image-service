# Instagram Image Service

FastAPI service for uploading images to S3 and storing metadata in DynamoDB. Local development uses [LocalStack](https://localstack.cloud/) so no real AWS account or environment variables are required.

## Architecture

```
Client  →  FastAPI (port 8000)  →  S3 (images-bucket)
                              →  DynamoDB (images table)
                                        ↑
                              LocalStack (port 4566)
```

| Component | LocalStack resource |
|-----------|-------------------|
| Image files | S3 bucket `images-bucket`, keys `images/{image_id}.{ext}` |
| Metadata | DynamoDB table `images` (partition key: `image_id`, GSI: `user_id-index`) |
| Presigned URLs | 1 hour expiry (`SIGNED_URL_EXPIRATION`) |

Configuration lives in `app/constants.py` (not environment variables).

## Prerequisites

- Python 3.9+
- Docker (for LocalStack)
- AWS CLI (optional, for inspecting S3/DynamoDB)

## Quick start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start LocalStack

```bash
docker compose up -d
```

Verify:

```bash
curl http://localhost:4566/_localstack/health
```

### 3. Run the API

```bash
uvicorn main:app --reload --port 8000
```

On startup, the app creates the S3 bucket and DynamoDB table if they do not exist.

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health: http://localhost:8000/

## API reference

### Health check

```http
GET /
```

### Upload image

```http
POST /images?user_id={user_id}&title={title}&tags={comma-separated-tags}
Content-Type: multipart/form-data
```

| Field | Location | Description |
|-------|----------|-------------|
| `file` | form | Image file (`image/jpeg`, `image/png`, `image/jpg`) |
| `user_id` | query | Owner identifier |
| `title` | query | Image title |
| `tags` | query | Comma-separated tags, e.g. `nature,travel` |

**Example**

```bash
curl -X POST "http://localhost:8000/images?user_id=user1&title=sunset&tags=nature,travel" \
  -F "file=@photo.jpg"
```

**Response** `201`

```json
{
  "image_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "uploaded successfully"
}
```

### List images

```http
GET /images?user_id=&tag=&limit=10&last_key=
```

| Query | Description |
|-------|-------------|
| `user_id` | Filter by user (uses DynamoDB GSI) |
| `tag` | Filter items whose `tags` list contains this value |
| `limit` | Page size (1–100, default 10) |
| `last_key` | URL-encoded JSON from previous `last_evaluated_key` for pagination |

**Example**

```bash
curl "http://localhost:8000/images?user_id=user1&limit=5"
```

### Get download URL

```http
GET /images/{image_id}
```

Returns a presigned S3 URL valid for one hour.

```json
{
  "image_id": "550e8400-e29b-41d4-a716-446655440000",
  "download_url": "http://localhost:4566/images-bucket/..."
}
```

### Delete image

```http
DELETE /images/{image_id}
```

Removes the S3 object and DynamoDB row.

## Verify data in LocalStack

Use port **4566** for AWS CLI (not **8000**, which is the API).

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

**S3**

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://images-bucket/ --recursive
```

**DynamoDB**

```bash
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name images
```

**Single item**

```bash
aws --endpoint-url=http://localhost:4566 dynamodb get-item \
  --table-name images \
  --key '{"image_id":{"S":"YOUR-IMAGE-ID"}}'
```

## Running tests

Tests require LocalStack on `localhost:4566`. They create bucket/table if needed and **clear all S3 objects and DynamoDB items before and after each test**.

```bash
pytest tests/ -v
```

## Project layout

```
app/
  constants.py      # Region, endpoint, bucket, table, credentials
  aws_setup.py      # Create bucket/table on API startup
  models/           # Pydantic request/response models
  routers/          # HTTP endpoints
  services/         # S3 and DynamoDB clients
main.py             # FastAPI app + lifespan
tests/
  conftest.py       # LocalStack setup and per-test cleanup
  test_image_router.py
docker-compose.yml  # LocalStack (S3 + DynamoDB)
```

## Configuration

Edit `app/constants.py` to change:

| Constant | Default | Purpose |
|----------|---------|---------|
| `AWS_ENDPOINT_URL` | `http://localhost:4566` | LocalStack endpoint |
| `S3_BUCKET_NAME` | `images-bucket` | S3 bucket |
| `DYNAMODB_TABLE_NAME` | `images` | DynamoDB table |
| `SIGNED_URL_EXPIRATION` | `3600` | Presigned URL TTL (seconds) |

For production AWS, point `AWS_ENDPOINT_URL` to real AWS (or `None` in boto3 clients) and use real credentials via IAM roles or configured profiles.

## Possible future improvements

- Authentication and per-user authorization
- File size limits and virus scanning
- Tag GSI for efficient tag queries (current tag filter is in-memory after scan)
- Structured logging and request IDs
- Deploy to ECS/Lambda with real AWS resources via Terraform or CDK
