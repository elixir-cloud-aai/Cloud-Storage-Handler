"""This module handles MinIO configuration and client initialization.

It provides functions to load MinIO configuration, initialize the MinIO client
with the configuration details, and perform operations such as bucket creation.
"""

from typing import Any, Dict

from minio import Minio

from cloud_storage_handler.minio_client import MinioClient


def initialize_minio_client(config: Dict[str, Any]) -> Minio:
    """Initialize the MinIO client with the given configuration.

    Args:
        config (Dict[str, Any]): A dictionary containing configuration details.

    Returns:
        Minio: A MinIO client instance.
    """
    endpoint = f"{config['hostname']}:{config['port']}"
    return Minio(
        endpoint,
        access_key=config["access_key"],
        secret_key=config["secret_key"],
        secure=config["is_secure"],
    )


def main():
    """Main function to load configuration and initialize the MinIO client."""
    minio_client = MinioClient()
    minio_client.create_bucket(minio_client.bucket_name)
    print(minio_client.client)
    return minio_client.client


minio_client = main()
