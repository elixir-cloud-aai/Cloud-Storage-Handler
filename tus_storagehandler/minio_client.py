"""MinIO Client Configuration Module.

This module initializes a MinIO client using environment variables.
It also provides a method to create a new MinIO
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


class MinioClient:
    """A class to manage MinIO client configuration and bucket creation."""

    def __init__(self):
        """Initialize the MinIO client using environment variables."""
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_IS_SECURE,
        )

    def create_bucket(self):
        """Create a new bucket if it does not already exist."""
        if not self.client.bucket_exists(MINIO_BUCKET):
            self.client.make_bucket(MINIO_BUCKET)


minio_client = MinioClient()
minio_client.create_bucket()
