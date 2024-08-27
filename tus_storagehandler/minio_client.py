"""MinIO Client Configuration Module.

This module initializes a MinIO client using environment variables.
It also provides a function to create a new MinIO
bucket if it does not already exist.
"""

from minio import Minio

from tus_storagehandler.consts import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_IS_SECURE,
    MINIO_SECRET_KEY,
)

minio_client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_IS_SECURE,
)


def create_bucket():
    """Creates a new bucket if it does not already exist.

    This function checks if the bucket specified by MINIO_BUCKET exists.
    If it does not exist, it creates a new bucket using the MinIO client instance.
    """
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)


create_bucket()
