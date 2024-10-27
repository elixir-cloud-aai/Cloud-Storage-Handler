"""ELIXIR's Cloud Storage Handler controllers."""

import logging
import os
import uuid
from http import HTTPStatus

from flask import current_app, jsonify, request
from minio.error import S3Error

logger = logging.getLogger(__name__)

CHUNK_SIZE = 5 * 1024 * 1024


def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK


def get_chunks(file_obj, chunk_size):
    """Generate chunks from a file object."""
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk

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
    upload_dir = "/tmp/upload"

    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if not file:
            return jsonify({"error": "No file provided"}), HTTPStatus.BAD_REQUEST

        file_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{file_id}.temp")

        with open(file_path, "wb") as f:
            file.save(f)

        total_size = os.path.getsize(file_path)
        total_chunks = (total_size // CHUNK_SIZE) + (
            1 if total_size % CHUNK_SIZE > 0 else 0
        )

        try:
            # Stream the file to disk in chunks for better performance with large files
            with open(file_path, "wb") as dest:
                for chunk in file.stream:
                    dest.write(chunk)

            total_size = os.path.getsize(file_path)
            total_chunks = (total_size // CHUNK_SIZE) + (
                1 if total_size % CHUNK_SIZE > 0 else 0
            )

            # Stream each chunk to Minio for upload
            with open(file_path, "rb") as f:
                for i, chunk in enumerate(get_chunks(f, CHUNK_SIZE)):
                    try:
                        minio_client.put_object(
                            bucket_name,
                            f"{file_id}/chunk_{i}",
                            chunk,
                            len(chunk),
                            metadata={"description": "Chunk upload via Flask"},
                        )
                    except S3Error as e:
                        logger.error(f"Failed to upload chunk {i} for file {file_id}: {str(e)}")
                        return jsonify({"error": "Failed to upload file to cloud storage"}), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            return jsonify({"error": "An error occurred while processing the file"}), HTTPStatus.INTERNAL_SERVER_ERROR
        finally:
            # Cleanup temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        responses.append(
            {
                "message": "File uploaded successfully",
                "file_id": file_id,
                "total_chunks": total_chunks,
            }
        )

    return jsonify(responses), HTTPStatus.OK
