# app/routers/image_router.py

import json
import logging
import uuid

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Query
from fastapi import HTTPException
from fastapi import status

from app.models.image_model import (
    UploadResponse,
    ImageMetadata,
    ImageDownloadResponse,
    DeleteResponse,
    ImageListResponse,
)

from app.services.s3_service import (
    upload_file,
    generate_download_url,
    delete_file
)

from app.services.dynamodb_service import (
    save_metadata,
    get_image,
    delete_metadata,
    list_images
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Images"]
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}


@router.post(
    "/images",
    summary="Upload image with metadata",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Query(...),
    title: str = Query(...),
    tags: str = Query(...)
):

    try:

        file_content = await file.read()

        if not file_content:

            raise HTTPException(
                status_code=400,
                detail="Image file is required"
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type"
            )

        if not file.filename or "." not in file.filename:
            raise HTTPException(
                status_code=400,
                detail="File must have a valid extension"
            )

        image_id = str(uuid.uuid4())

        tag_list = [
            tag.strip()
            for tag in tags.split(",")
            if tag.strip()
        ]

        extension = file.filename.rsplit(".", 1)[-1].lower()

        s3_key = f"images/{image_id}.{extension}"

        upload_file(
            key=s3_key,
            body=file_content,
            content_type=file.content_type,
        )

        metadata = ImageMetadata(
            image_id=image_id,
            user_id=user_id,
            title=title,
            tags=tag_list,
            s3_key=s3_key,
            created_at=datetime.now(timezone.utc).isoformat()
        )

        try:
            save_metadata(
                metadata.model_dump()
            )
        except Exception:
            delete_file(s3_key)
            raise

        return UploadResponse(
            image_id=image_id,
            message="uploaded successfully"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images",
    response_model=ImageListResponse
)
async def get_all_images(
    user_id: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    last_key: Optional[str] = None
):

    try:

        exclusive_start_key = None

        if last_key:
            try:
                exclusive_start_key = json.loads(last_key)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="last_key must be valid JSON from a previous response"
                )

        result = list_images(
            user_id=user_id,
            tag=tag,
            limit=limit,
            last_key=exclusive_start_key
        )

        return ImageListResponse(
            items=[ImageMetadata(**item) for item in result["items"]],
            last_evaluated_key=result.get("last_evaluated_key"),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("List images failed")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images/{image_id}",
    response_model=ImageDownloadResponse
)
async def fetch_image(image_id: str):

    try:

        item = get_image(image_id)

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )

        download_url = generate_download_url(
            item["s3_key"]
        )

        return ImageDownloadResponse(
            image_id=image_id,
            download_url=download_url
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Fetch image failed")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete(
    "/images/{image_id}",
    response_model=DeleteResponse
)
async def remove_image(image_id: str):

    try:

        item = get_image(image_id)

        if not item:

            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )

        delete_file(
            item["s3_key"]
        )

        delete_metadata(
            image_id
        )

        return DeleteResponse(
            message="Image deleted successfully"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Delete image failed")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
