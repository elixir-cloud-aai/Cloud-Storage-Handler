"""MinIO client class and convenience functions."""

import logging

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
        self.client: Minio = Minio(
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
        app: Connexion Flask app instance.

    Returns:
        Connexion Flask app instance with a MinIO client instance added to
            its config.
    """
    minio_client = MinioClient(config=app.app.config.foca.custom.minio)
    minio_client.create_bucket()
    app.app.config.foca.custom.minio.client = minio_client
    logger.info("MinIO client registered.")
    return app
