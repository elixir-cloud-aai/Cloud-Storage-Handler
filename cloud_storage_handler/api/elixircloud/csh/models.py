"""Model for MinIO Configuration."""

from typing import Annotated

from pydantic import BaseModel, conint, constr


class MinioConfig(BaseModel):
    """Configuration for MinIO.

    Attributes:
        hostname : The hostname where the MinIO server is running.
                        Defaults to 'localhost'.
        port (int): The port on which the MinIO server is running.
                        Must be between 1 and 65535. Defaults to 9000.
        access_key (str): The access key used for authentication with MinIO.
                            Defaults to 'minioadmin'.
        secret_key (str): The secret key used for authentication with MinIO.
                            Defaults to 'minioadmin'.
        bucket_name (str): The name of the bucket where files are stored.
                                Must be at least 1 character long. Defaults to 'files'.

    Examples:
        MinioConfig(
            hostname="localhost",
            port=9000,
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket_name="files",
            secure=False
        )
    """

    hostname: str = "localhost"
    port: Annotated[int, conint(ge=1, le=65535)] = 9000
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket_name: Annotated[str, constr(min_length=1)] = "files"
    secure: bool = False
