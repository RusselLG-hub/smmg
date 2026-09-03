from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from minio.error import S3Error

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
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

    url = f"{settings.API_PUBLIC_URL.rstrip('/')}/v1/uploads/{stored_name}"

    return UploadResponse(object_name=stored_name, url=url)


def get_uploaded_file(object_path: str) -> StreamingResponse:
    try:
        response = minio_provider.get_file(object_path)
    except S3Error as err:
        if err.code in ("NoSuchKey", "NoSuchBucket"):
            raise NotFoundException(detail="File not found")
        raise

    content_type = response.headers.get("content-type") or "application/octet-stream"
    content_length = response.headers.get("content-length")
    etag = response.headers.get("etag")

    headers = {
        "Cache-Control": "public, max-age=86400",
    }
    if content_length:
        headers["Content-Length"] = str(content_length)
    if etag:
        headers["ETag"] = str(etag)

    def iterfile():
        try:
            for chunk in response.stream(32 * 1024):
                yield chunk
        finally:
            response.close()
            response.release_conn()

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers=headers,
    )

