"""Custom configuration model for the FOCA app."""

from pydantic import BaseModel

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig


class CustomConfig(BaseModel):
    """Custom configuration model for the FOCA app.

    Attributes:
        and access credentials.
    """

    minio: MinioConfig
