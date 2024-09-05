"""This module handles the loading of environment variables for MinIO configuration."""

from cloud_storage_handler.minio_client import MinioClient


def GetMinioConfiguration():  # type: ignore
    """Get minio configuration."""
    minio_config = MinioClient()
    return minio_config.response()


minio_config_data = GetMinioConfiguration()

MINIO_HOSTNAME = minio_config_data["hostname"]
MINIO_PORT = minio_config_data["port"]
MINIO_ENDPOINT = f"{MINIO_HOSTNAME}:{MINIO_PORT}"
MINIO_SECURE = minio_config_data["is_secure"]

minio_client_instance = MinioClient()
minio_client = minio_client_instance.initialise_minio(
    endpoint=MINIO_ENDPOINT,
    access_key=minio_config_data["access_key"],
    secret_key=minio_config_data["secret_key"],
    secure=MINIO_SECURE,
)

minio_client_instance.create_bucket(minio_config_data["bucket_name"])
