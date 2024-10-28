"""ELIXIR's Cloud Storage Handler controllers."""

import hashlib
import logging
import os
import tempfile
import uuid
from http import HTTPStatus

from flask import current_app, jsonify, request
from minio import S3Error

logger = logging.getLogger(__name__)

TUS_UPLOAD_DIR = tempfile.gettempdir()


def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK


def compute_file_hash(file_path):
    """Compute SHA-256 hash of the file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def initiate_upload():
    """Initiate TUS upload, creates object and returns object_id."""
    object_id = str(uuid.uuid4())
    object_path = os.path.join(TUS_UPLOAD_DIR, f"{object_id}.temp")
    os.makedirs(TUS_UPLOAD_DIR, exist_ok=True)

    open(object_path, "wb").close()

    return jsonify({"object_id": object_id}), HTTPStatus.CREATED


def upload_chunk(object_id):
    """Upload a object chunk based on object_id and content-range."""
    if request.method == "OPTIONS":
        response = jsonify({"status": "CORS preflight check"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )

    object_path = os.path.join(TUS_UPLOAD_DIR, f"{object_id}.temp")
    if not os.path.exists(object_path):
        return jsonify({"error": "object not found"}), HTTPStatus.NOT_FOUND

    try:
        content_range = request.headers.get("Content-Range")
        start_byte = int(content_range.split(" ")[1].split("-")[0])

        with open(object_path, "r+b") as f:
            f.seek(start_byte)
            f.write(request.data)

        return jsonify(
            {"message": "Chunk uploaded successfully"}
        ), HTTPStatus.NO_CONTENT
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


def complete_upload(object_id):
    """Complete upload by transferring the object to MinIO after TUS upload."""
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client
    object_path = os.path.join(TUS_UPLOAD_DIR, f"{object_id}.temp")

    if not os.path.exists(object_path):
        return jsonify({"error": "object not found"}), HTTPStatus.NOT_FOUND

    try:
        # Compute the file's hash
        file_hash = compute_file_hash(object_path)

        # Check if an object with the same hash exists in MinIO
        found_duplicate = False
        for obj in minio_client.list_objects(bucket_name):
            obj_info = minio_client.stat_object(bucket_name, obj.object_name)
            if (
                "file-hash" in obj_info.metadata
                and obj_info.metadata["file-hash"] == file_hash
            ):
                found_duplicate = True
                break

        if found_duplicate:
            os.remove(object_path)
            return jsonify(
                {"message": "Duplicate object detected. Upload skipped."}
            ), HTTPStatus.CONFLICT

        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_id,
            file_path=object_path,
            content_type="application/octet-stream",
        )

        os.remove(object_path)

        return jsonify(
            {"message": "Upload complete and object stored in MinIO"}
        ), HTTPStatus.OK

    except S3Error as e:
        return jsonify(
            {"error": f"Failed to upload to MinIO: {str(e)}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
