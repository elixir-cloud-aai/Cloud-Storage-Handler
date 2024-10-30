"""ELIXIR's Cloud Storage Handler controllers."""

import logging

from flask import current_app
from foca.utils.logging import log_traffic  # type: ignore

from cloud_storage_handler.api.elixircloud.csh.tus.tus import TusController

logger = logging.getLogger(__name__)


@log_traffic
def upload_object():
    """Upload an object to the storage."""
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload()


@log_traffic
def object_upload_chunk_head(resourceId):
    """Handle HEAD request for chunk upload."""
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)


@log_traffic
def object_upload_chunk_patch(resourceId):
    """Handle PATCH request for chunk upload."""
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)


@log_traffic
def object_upload_chunk_delete(resourceId):
    """Handle DELETE request for chunk upload."""
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    tus = TusController(minio_client, bucket_name)
    return tus.tus_object_upload_chunk(resourceId)
