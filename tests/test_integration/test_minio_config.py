"""Integration tests for the minio configuration."""

import pytest
from minio import Minio
from pydantic import ValidationError
from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig

def test_create_minio_client():
    config = MinioConfig()
    client = Minio(
        endpoint=f"{config.hostname}:{config.port}",
        access_key=config.access_key,
        secret_key=config.secret_key,
        secure=config.secure,
    )
    config.client = client
    assert isinstance(config.client, Minio)
