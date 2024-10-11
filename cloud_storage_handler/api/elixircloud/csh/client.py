"""MinIO client class and convenience functions."""

import logging
from typing import Type

from connexion import FlaskApp
from minio import Minio

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig

logger = logging.getLogger(__name__)


class MinioClient:
    """Client for MinIO operations.

    Wraps ``minio.Minio`` and adds convenience methods.

    Attributes:
        config: MinIO configuration.
        client: MinIO client instance.
    """

    def __init__(self, config: MinioConfig) -> None:
        """Class constructor.

        Args:
            config: MinIO configuration.
        """
        self.config: MinioConfig = config
        self.client: Type[Minio] = Minio(
            endpoint=f"{config.hostname}:{config.port}",
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )

    def create_bucket(self) -> None:
        """Create bucket if it does not exist."""
        if not self.client.bucket_exists(self.config.bucket_name):
            self.client.make_bucket(self.config.bucket_name)
            logger.info(f"Bucket '{self.config.bucket_name}' created.")
        else:
            logger.debug(f"Bucket '{self.config.bucket_name}' already exists.")


def register_minio_client(app: FlaskApp) -> FlaskApp:
    """Register MinIO client and create bucket.

    Args:
        app: FOCA app instance.

    Returns:
        FOCA app instance with MinIO client instance added to config.
    """
    minio_config = app.app.config.foca.custom.minio
    minio_client = MinioClient(config=minio_config)
    minio_client.create_bucket()
    minio_config.client = minio_client
    logger.info("MinIO client registered.")
    return app
