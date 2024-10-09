"""CSH scoped constants."""

from pydantic import BaseModel

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig


class CshConstants(BaseModel):
    """All the constants related to CSH and related services.

    Attributes:
        foca_config_path: Path to FOCA configuration for CSH.
        minio_constants: Constants related to MinIO configuration.
    """

    foca_config_path: str = "CSH_FOCA_CONFIG_PATH"
    default_minio_config: MinioConfig = MinioConfig(
        hostname="localhost",
        port=9000,
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="files",
        secure=False,
    )

    class Config:
        """Configuration for CshConstants class."""

        frozen = True


chs_constants = CshConstants()
