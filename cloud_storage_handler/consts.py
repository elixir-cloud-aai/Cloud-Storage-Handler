"""This module handles the loading of environment variables for MinIO configuration."""

from typing import Dict

from minio import Minio

from cloud_storage_handler.minio_client import MinioClient


def load_minio_config() -> Dict[str, any]:
    """Load MinIO configuration.

    Returns:
        Dict[str, any]: A dictionary containing MinIO configuration details.
    """
    minio_client = MinioClient()
    return minio_client.get_minio_config()


def initialize_minio_client(config: Dict[str, any]) -> Minio:
    """Initialize the MinIO client with the given configuration.

    Args:
        config (Dict[str, any]): A dictionary containing configuration details.

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
