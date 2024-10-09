"""This module provides functionality for managing MinIO client."""

import logging

from foca import Foca
from minio import Minio

from cloud_storage_handler.api.elixircloud.csh.constants import chs_constants
from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig
from cloud_storage_handler.custom_config import CustomConfig
from cloud_storage_handler.utils import get_config_path

logger = logging.getLogger(__name__)


class MinioConfigurationData:
    """Handles the loading and parsing of MinIO configuration files."""

    def __init__(self, config_file=None):
        """Initialize MinioConfig with a configuration file.

        Args:
            config_file : Path to the configuration file. If not provided,
                               uses the default path.
        """
        config_file = config_file or get_config_path()
        self.config: CustomConfig = Foca(config_file=config_file).conf

    def get_minio_config(self) -> MinioConfig:
        """Retrieve the MinIO configuration.

        Returns:
            A dictionary containing the MinIO configuration.
        """
        minio_from_foca_config = self.config.minio
        return MinioConfig(
            hostname=getattr(
                minio_from_foca_config,
                "hostname",
                chs_constants.default_minio_config.hostname,
            ),
            port=getattr(
                minio_from_foca_config, "port", chs_constants.default_minio_config.port
            ),
            access_key=getattr(
                minio_from_foca_config,
                "access_key",
                chs_constants.default_minio_config.access_key,
            ),
            secret_key=getattr(
                minio_from_foca_config,
                "secret_key",
                chs_constants.default_minio_config.secret_key,
            ),
            bucket_name=getattr(
                minio_from_foca_config,
                "bucket_name",
                chs_constants.default_minio_config.bucket_name,
            ),
            secure=getattr(
                minio_from_foca_config,
                "secure",
                chs_constants.default_minio_config.secure,
            ),
        )


class MinioClient:
    """A class to manage MinIO client configuration and bucket creation."""

    def __init__(self):
        """Initialize the MinIO client and create bucket if necessary."""
        config = MinioConfigurationData().get_minio_config()
        self.client = Minio(
            endpoint=f"{config.hostname}:{config.port}",
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )
        self.bucket_name = config.bucket_name

        # Create bucket if it doesn't exist
        self.create_bucket()

    def create_bucket(self):
        """Creation of bucket using the configured bucket name."""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' created.")
        else:
            logger.info(f"Bucket '{self.bucket_name}' already exists.")

    def get_client(self):
        """Return the MinIO client."""
        return self.client
