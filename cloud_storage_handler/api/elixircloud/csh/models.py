"""Model for MinIO Configuration."""

from typing import Annotated

from pydantic import BaseModel, Field, constr


class MinioConfig(BaseModel):
    """Configuration for MinIO."""

    hostname: str = Field(
        ...,
        description="The hostname where the MinIO server is running.",
        example="localhost",
    )
    port: int = Field(
        ...,
        description="The port on which the MinIO server is running.",
        example=9000,
        ge=1,
        le=65535,
    )
    access_key: str = Field(
        ...,
        description="The access key used for authentication with MinIO.",
        example="minioadmin",
    )
    secret_key: str = Field(
        ...,
        description="The secret key used for authentication with MinIO.",
        example="minioadmin",
    )
    is_secure: bool = Field(
        ...,
        description=(
            "Specifies whether the connection to MinIO should be secure (HTTPS)."
        ),
        example=False,
    )
    bucket_name: Annotated[str, constr(min_length=1)] = Field(
        ...,
        description="The name of the bucket where files are stored.",
        example="files",
    )
