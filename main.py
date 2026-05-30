# main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.aws_setup import ensure_localstack_resources
from app.routers.image_router import router as image_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_localstack_resources()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Instagram Image Service",
    description="""
Scalable image upload and metadata management service.

Features:
- Upload image with metadata
- List images with filters
- Download/view image
- Delete image
- S3 object storage
- DynamoDB metadata persistence
""",
    version="1.0.0"
)

app.include_router(
    image_router
)


@app.get("/")
async def health_check():

    return {
        "status": "healthy",
        "service": "instagram-image-service"
    }