"""Minio client module.

This module provides functionality to interact with the Minio cloud storage
service.
"""

from cloud_storage_handler.clients.minio_client import MinioClient


def get_minio_client():
    """Get a Minio client and create a bucket.

    Returns:
        MinioClient: An initialized Minio client with a created bucket.
    """
    client = MinioClient()
    client.create_bucket()
    return client
