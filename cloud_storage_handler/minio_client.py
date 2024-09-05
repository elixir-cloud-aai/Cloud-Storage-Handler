"""This module provides functionality for managing MinIO client."""

import logging

from foca import Foca
from minio import Minio

from cloud_storage_handler.exceptions import ConfigNotFoundError
from cloud_storage_handler.utils import get_config_path

logger = logging.getLogger(__name__)


class MinioClient:
    """A class to manage MinIO client configuration and bucket creation."""

    def __init__(self) -> None:
        """Initializes the MinIO client class."""
        self.minio_config_data = None
        self.config = Foca(config_file=get_config_path()).conf
        self.client = None  # MinIO client will be initialized later

    def initialise_minio(self, endpoint, access_key, secret_key, secure):
        """Initialize the MinIO client with provided configurations."""
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,  # Correctly use the secure flag
        )
        return self.client

    def create_bucket(self, bucket_name):
        """Create a new bucket if it does not already exist."""
        if self.client is None:
            raise RuntimeError("MinIO client is not initialized.")

        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def get_default_minio_config(self):
        """Get the default minio configuration."""
        logger.warning(
            "Minio configuration not found in config. Using default configuration."
        )
        return {
            "hostname": "localhost",
            "port": 9000,
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "is_secure": False,
            "bucket_name": "files",
        }

    def get_minio_from_config(self):
        """Returns minio configuration from config."""
        if not self.config.custom:
            raise ConfigNotFoundError("Custom configuration not found.")

        minio_config_data = self.config.custom.get("minio")
        if not minio_config_data:
            raise ConfigNotFoundError("Service info not found in custom configuration.")

        return minio_config_data

    def response(self):
        """Returns minio configuration response."""
        if self.minio_config_data is None:
            try:
                self.minio_config_data = self.get_minio_from_config()
            except ConfigNotFoundError:
                self.minio_config_data = self.get_default_minio_config()

        return self.minio_config_data
