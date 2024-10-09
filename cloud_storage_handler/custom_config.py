"""Custom configuration model for the FOCA app."""

from pydantic import BaseModel

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig


class CustomConfig(BaseModel):
    """Custom configuration model for the FOCA app.

    Attributes:
        minio: Minio configurations, scuh as hostname, port, access_key, secret_key,
            and bucket_name.
    """

    # Define custom configuration fields here
    minio: MinioConfig
