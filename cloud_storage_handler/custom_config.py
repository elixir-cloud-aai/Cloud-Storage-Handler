"""Custom configuration model for the FOCA app."""

from pydantic import BaseModel

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig


class CustomConfig(BaseModel):
    """Custom configuration model for the FOCA app.

    Attributes:
        minio (MinioConfig): Configuration for MinIO, including bucket details
        and access credentials.
    """

    minio: MinioConfig
