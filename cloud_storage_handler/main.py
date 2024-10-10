"""API server entry point."""

import logging
import os
import sys
from pathlib import Path

from connexion import FlaskApp
from foca import Foca
from minio import Minio
from pydantic import ValidationError

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig
from cloud_storage_handler.custom_config import CustomConfig

logger = logging.getLogger(__name__)


def init_app() -> tuple[FlaskApp, MinioConfig]:
    """Initialize and return the FOCA app and MinIO configuration."""
    # Determine the configuration path
    if config_path_env := os.getenv("CSH_FOCA_CONFIG_PATH"):
        config_path = Path(config_path_env).resolve()
    else:
        config_path = (
            Path(__file__).parents[1] / "deployment" / "config.yaml"
        ).resolve()

    # Check if the configuration file exists
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    foca = Foca(
        config_file=config_path,
        custom_config_model="cloud_storage_handler.custom_config.CustomConfig",
    )
    foca_config = foca.conf
    try:
        custom_config_data = foca_config.custom.dict()
        custom_config = CustomConfig(**custom_config_data)
    except ValidationError as e:
        logger.error(f"Error parsing custom configuration: {e}")
        raise
    minio_config = custom_config.minio

    # Create the Connexion FlaskApp instance
    return foca.create_app(), minio_config


def main() -> None:
    """Run FOCA application."""
    try:
        app, minio_config = init_app()
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        sys.exit(1)
    foca_app = app.app

    # Initialize MinIO client
    try:
        minio_client = Minio(
            endpoint=f"{minio_config.hostname}:{minio_config.port}",
            access_key=minio_config.access_key,
            secret_key=minio_config.secret_key,
            secure=minio_config.secure,
        )
        foca_app.config["minio_client"] = minio_client
    except Exception as e:
        logger.error(f"Error initializing MinIO client: {e}")
        return

    # Check if the bucket exists and create it if it doesn't
    bucket_name = minio_config.bucket_name
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created.")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists.")
    except Exception as e:
        logger.error(f"Error checking or creating bucket: {e}")
        return

    # Start the Flask app
    app.run(port=app.port)


if __name__ == "__main__":
    main()
