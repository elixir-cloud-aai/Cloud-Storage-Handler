"""ELIXIR's Cloud Storage Handler controllers."""

import logging
import os
import uuid
from http import HTTPStatus

from flask import current_app, jsonify, request
from minio.error import S3Error

logger = logging.getLogger(__name__)

UPLOAD_DIRECTORY = "/tmp/upload"
CHUNK_SIZE = 5 * 1024 * 1024


def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK


def upload_object():
    """Handles file uploads to cloud storage.

    Retrieves files from the request, processes each file into chunks,
    and uploads them to the specified storage bucket. Returns a response
    with a success message and details about the uploaded file(s).
    """
    files = request.files.getlist("files")
    responses = []
    minio_config = current_app.config.foca.custom.minio
    bucket_name = minio_config.bucket_name
    minio_client = current_app.config.foca.custom.minio.client.client

    for file in files:
        if not file:
            return jsonify({"error": "No file provided"}), 400

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{file_id}.temp")

        file.save(file_path)

        total_size = os.path.getsize(file_path)
        total_chunks = (total_size // CHUNK_SIZE) + (
            1 if total_size % CHUNK_SIZE > 0 else 0
        )

        file_dir = os.path.join(UPLOAD_DIRECTORY, file_id)
        os.makedirs(file_dir, exist_ok=True)

        with open(file_path, "rb") as f:
            for i in range(total_chunks):
                chunk_data = f.read(CHUNK_SIZE)
                chunk_filename = os.path.join(file_dir, f"chunk_{i}")
                with open(chunk_filename, "wb") as chunk_file:
                    chunk_file.write(chunk_data)

                try:
                    minio_client.fput_object(
                        bucket_name,
                        f"{file_id}/chunk_{i}",
                        chunk_filename,
                        metadata={
                            "description": "Chunk upload via Flask",
                        },
                    )
                except S3Error as e:
                    return jsonify({"error": str(e)}), 500

        os.remove(file_path)
        os.rmdir(file_dir)

        responses.append(
            {
                "message": "File uploaded successfully",
                "file_id": file_id,
                "total_chunks": total_chunks,
            }
        )

    return jsonify(responses), 200
