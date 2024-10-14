"""ELIXIR's Cloud Storage Handler controllers."""

import logging
from http import HTTPStatus

from flask import current_app, jsonify
from minio.error import S3Error

logger = logging.getLogger(__name__)


def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK


def list_files():
    """Endpoint to list all files in the MinIO bucket."""
    try:
        minio_config = current_app.config.foca.custom.minio
        bucket_name = minio_config.bucket_name
        minio_client = current_app.config.foca.custom.minio.client.client
        objects = minio_client.list_objects(bucket_name)
        files = [obj.object_name for obj in objects]
        return jsonify({"files": files}), 200

    except S3Error as err:
        return jsonify({"error": str(err)}), 500
