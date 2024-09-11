"""ELIXIR's Cloud Storage Handler controllers."""

import logging
from http import HTTPStatus

from flask import jsonify
from minio.error import S3Error

from cloud_storage_handler.clients.minio import get_minio_client

logger = logging.getLogger(__name__)


def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK


def list_files():
    """Endpoint to list all files in the MinIO bucket."""
    try:
        minio_client = get_minio_client()
        objects = minio_client.list_objects("files")
        files = [obj.object_name for obj in objects]
        return jsonify({"files": files}), 200

    except S3Error as err:
        return jsonify({"error": str(err)}), 500
