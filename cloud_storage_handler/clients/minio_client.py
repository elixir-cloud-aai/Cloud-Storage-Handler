"""This module provides functionality for managing MinIO client."""

import logging

from foca import Foca
from minio import Minio

from cloud_storage_handler.exceptions import ConfigNotFoundError
from cloud_storage_handler.utils import get_config_path

logger = logging.getLogger(__name__)


class MinioConfig:
    """Handles the loading and parsing of MinIO configuration files."""

    def __init__(self, config_file=None):
        """Initialize MinioConfig with a configuration file.

        Args:
            config_file (str): Path to the configuration file. If not provided,
                               uses the default path.
        """
        config_file = config_file or get_config_path()
        self.config = Foca(config_file=config_file).conf

    def get_minio_config(self):
        """Retrieve the MinIO configuration.

        Returns:
            dict: A dictionary containing the MinIO configuration.
        """
        try:
            return self.get_minio_from_config()
        except ConfigNotFoundError:
            return self.get_default_minio_config()

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
            "bucket_name": "files",
        }

    def get_minio_from_config(self):
        """Returns minio configuration from config."""
        if not self.config.custom:
            raise ConfigNotFoundError("Custom configuration not found.")

        minio_config_data = self.config.custom.get("minio")
        if not minio_config_data:
            raise ConfigNotFoundError(
                "MinIO configuration not found in custom configuration."
            )

        return minio_config_data


class MinioClient:
    """A class to manage MinIO client configuration and bucket creation."""

    def __init__(self):
        """Initialize the MinIO client and create bucket if necessary."""
        config = MinioConfig().get_minio_config()
        self.client = self.initialise_minio(
            endpoint=f"{config['hostname']}:{config['port']}",
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=False,
        )
        self.bucket_name = config["bucket_name"]

    def initialise_minio(self, endpoint, access_key, secret_key, secure):
        """Initialize the MinIO client with provided configurations."""
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )
        return self.client

    def create_bucket(self):
        """Creation of bucket using the configured bucket name."""
        if self.client is None:
            raise RuntimeError("MinIO client is not initialized.")

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' created.")
        else:
            logger.info(f"Bucket '{self.bucket_name}' already exists.")
