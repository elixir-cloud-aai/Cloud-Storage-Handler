"""ELIXIR's Cloud Storage Handler controllers."""

import logging
from flask import current_app, Response
from foca.utils.logging import log_traffic  # type: ignore

from cloud_storage_handler.api.elixircloud.csh.tus.tus import TusController

logger = logging.getLogger(__name__)

@log_traffic
def upload_object() -> Response:
    """Upload an object to the storage.

    This function handles the upload of an object to the specified
    storage bucket using the Tus protocol.

    Returns:
        Response: The Flask response object containing the result of the upload.
    """
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload()


@log_traffic
def object_upload_chunk_head(resourceId: str) -> Response:
    """Handle HEAD request for chunk upload.

    This function processes HEAD requests for chunk uploads.

    Args:
        resourceId (str): The unique identifier for the resource being uploaded.

    Returns:
        Response: The Flask response object containing the status of the upload.
    """
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)


@log_traffic
def object_upload_chunk_patch(resourceId: str) -> Response:
    """Handle PATCH request for chunk upload.

    This function processes PATCH requests to upload chunks of an object.

    Args:
        resourceId (str): The unique identifier for the resource being uploaded.

    Returns:
        Response: The Flask response object containing the status of the upload.
    """
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)


@log_traffic
def object_upload_chunk_delete(resourceId: str) -> Response:
    """Handle DELETE request for chunk upload.

    This function processes DELETE requests for uploaded chunks.

    Args:
        resourceId (str): The unique identifier for the resource being uploaded.

    Returns:
        Response: The Flask response object confirming the deletion.
    """
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)
