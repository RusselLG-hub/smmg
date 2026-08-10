from fastapi import UploadFile

from app.core.exceptions import BadRequestException
from app.features.v1.uploads.schema import UploadResponse
from app.helpers.ulid import generate_ulid
from app.providers import minio_provider

ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_image(file: UploadFile) -> UploadResponse:
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestException(
            detail="Invalid image format. Allowed formats: JPEG, PNG, WebP, GIF."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise BadRequestException(detail="File size exceeds maximum limit of 5MB.")

    ext = ALLOWED_MIME_TYPES[file.content_type]
    object_name = f"images/{generate_ulid()}.{ext}"

    stored_name = minio_provider.upload_file(
        object_name=object_name,
        data=content,
        content_type=file.content_type,
    )

    try:
        url = minio_provider.get_presigned_url(stored_name, expires_hours=24)
    except Exception:
        url = f"/v1/uploads/{stored_name}"

    return UploadResponse(object_name=stored_name, url=url)
