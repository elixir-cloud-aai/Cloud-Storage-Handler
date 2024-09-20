"""Constants."""

from pydantic import BaseModel

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig


class MinioConstants(BaseModel):
    """All the constants related to MinIO for CSH."""

    hostname: str = "localhost"
    port: int = 9000
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket_name: str = "files"

    class Config:
        """Configuration for MinioConstants class."""

        frozen = True


class CshConstants(BaseModel):
    """All the constants related to CSH and related services.

    Attributes:
        foca_config_path: Path to FOCA configuration for CSH.
        minio_constants: Constants related to MinIO configuration.
    """

    foca_config_path: str = "CSH_FOCA_CONFIG_PATH"
    minio_constants: MinioConstants = MinioConstants()

    class Config:
        """Configuration for CshConstants class."""

        frozen = True

    def get_minio_config(self) -> MinioConfig:
        """Return MinIO configuration as a Pydantic model."""
        minio_config = self.minio_constants
        return MinioConfig(
            hostname=minio_config.hostname,
            port=minio_config.port,
            access_key=minio_config.access_key,
            secret_key=minio_config.secret_key,
            bucket_name=minio_config.bucket_name,
        )
