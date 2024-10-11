"""Model for MinIO Configuration."""

from typing import Annotated, Optional, Type

from minio import Minio
from pydantic import BaseModel, conint, constr


class MinioConfig(BaseModel):
    """Configuration for MinIO.

    Attributes:
        hostname: The name of the host where the MinIO server is running.
        port: The port on which the MinIO server is running. Must be between 1
            and 65535.
        access_key: The access key used for authentication with MinIO.
        secret_key: The secret key used for authentication with MinIO.
        bucket_name: The name of the bucket where files are stored. Must be at
            least 1 character long.
        secure: Whether to use TLS connection to storage service or not.
        client: Client instance.

    Examples:
        MinioConfig(
            hostname="localhost",
            port=9000,
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket_name="files",
            secure=False,
        )
    """

    hostname: str = "localhost"
    port: Annotated[int, conint(ge=1, le=65535)] = 9000
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket_name: Annotated[str, constr(min_length=1)] = "files"
    secure: bool = False
    client: Optional[Type[Minio]] = None
