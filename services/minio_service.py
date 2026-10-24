from datetime import timedelta

from minio import Minio


BUCKET = "publications"

minio_client = Minio(
    "127.0.0.1:9000",
    access_key="admin",
    secret_key="admin12345",
    secure=False,
)


def get_media_url(filename: str | None):
    if not filename:
        return None

    return minio_client.presigned_get_object(
        BUCKET,
        filename,
        expires=timedelta(hours=1),
    )