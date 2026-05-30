from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class ImageMetadata(BaseModel):

    image_id: str
    user_id: str
    title: str
    tags: List[str]
    s3_key: str
    created_at: str


class UploadResponse(BaseModel):

    image_id: str
    message: str


class ImageDownloadResponse(BaseModel):

    image_id: str
    download_url: str


class DeleteResponse(BaseModel):

    message: str


class ImageListResponse(BaseModel):

    items: List[ImageMetadata]
    last_evaluated_key: Optional[Dict[str, Any]] = None