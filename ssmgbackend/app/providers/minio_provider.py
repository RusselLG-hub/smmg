from datetime import timedelta
from io import BytesIO

from minio import Minio

from app.core.config import settings

minio_client = Minio(
    endpoint=settings.minio_endpoint,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)

minio_public_client = Minio(
    endpoint=settings.MINIO_PUBLIC_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


def ensure_bucket() -> None:
    if not minio_client.bucket_exists(settings.MINIO_BUCKET):
        minio_client.make_bucket(settings.MINIO_BUCKET)


def upload_file(
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    ensure_bucket()
    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_name


def get_presigned_url(object_name: str, expires_hours: int = 1) -> str:
    return minio_public_client.presigned_get_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        expires=timedelta(hours=expires_hours),
    )


def delete_file(object_name: str) -> None:
    minio_client.remove_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
    )
