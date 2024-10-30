"""TUS-based file upload controller with MinIO."""

import base64
import hashlib
import io
import json
import logging
import uuid

from flask import current_app, make_response, request
from minio.error import S3Error

logger = logging.getLogger(__name__)


class TusController:
    """Controller for handling TUS-based file uploads using MinIO as backend storage."""

    def __init__(self, minio_client, bucket_name):
        """Initialize TusController with MinIO client and bucket name.

        Args:
            minio_client: MinIO client for interacting with the storage.
            bucket_name: Name of the bucket in MinIO to store files.
        """
        self.minio_client = minio_client
        self.bucket_name = bucket_name
        self.tus_api_version = "1.0.0"
        self.tus_api_version_supported = "1.0.0"
        self.tus_api_extensions = ["creation", "expiration", "termination"]
        self.tus_max_object_size = 50 * 1024 * 1024 * 1024  # 50 GB
        self.object_overwrite = False
        self.upload_url = "elixircloud/csh/v1/object"

    def compute_sha256(self, data):
        """Compute the SHA-256 checksum of the provided data.

        Args:
            data: Byte data to calculate the checksum for.

        Returns:
            str: SHA-256 hash of the data as a hexadecimal string.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()

    # def tus_object_upload(self):
    #     """Handle TUS protocol for object upload operations.

    #     Supports various HTTP methods:
    #         - HEAD: Checks object status or retrieves upload offset.
    #         - GET: Fetches metadata or checks object existence.
    #         - OPTIONS: Provides TUS protocol options.
    #         - POST/PUT: Handles new object upload.

    #     Returns:
    #         Flask response: Response indicating success or error.
    #     """
    #     response = make_response("", 200)

    #     if request.method == "HEAD":
    #         return self.handle_head_request(response)

    #     elif request.method == "GET":
    #         return self.handle_get_request(response)

    #     elif (
    #         request.method == "OPTIONS"
    #         and request.headers.get("Access-Control-Request-Method", None) is not None
    #     ):
    #         return response

    #     # Handle general TUS upload methods and responses
    #     if request.headers.get("Tus-Resumable") is not None:
    #         response.headers["Tus-Resumable"] = self.tus_api_version
    #         response.headers["Tus-Version"] = self.tus_api_version_supported

    #         if request.method == "OPTIONS":
    #             response.headers["Tus-Extension"] = ",".join(self.tus_api_extensions)
    #             response.headers["Tus-Max-Size"] = self.tus_max_object_size
    #             response.status_code = 204
    #             return response

    #         metadata = {}
    #         upload_metadata = request.headers.get("Upload-Metadata", None)
    #         if upload_metadata:
    #             for kv in upload_metadata.split(","):
    #                 key, value = kv.split(" ")
    #                 metadata[key] = base64.b64decode(value).decode("utf-8")

    #         if not self.object_overwrite:
    #             try:
    #                 incoming_sha256 = self.compute_sha256(request.data)

    #                 for obj in self.minio_client.list_objects(
    #                     self.bucket_name, recursive=True
    #                 ):
    #                     existing_data = self.minio_client.get_object(
    #                         self.bucket_name, obj.object_name
    #                     )
    #                     existing_sha256 = self.compute_sha256(existing_data.read())
    #                     existing_data.close()

    #                     if existing_sha256 == incoming_sha256:
    #                         response.status_code = 409
    #                         response.data = json.dumps(
    #                             {
    #                                 "message": (
    #                                     "Object with the same content already exists."
    #                                 ),
    #                                 "objectname": obj.object_name,
    #                             }
    #                         )
    #                         response.headers["Content-Type"] = "application/json"
    #                         return response

    #             except S3Error as e:
    #                 if e.code != "NoSuchKey":
    #                     response.status_code = 500
    #                     return response

    #         resource_id = str(uuid.uuid4())

    #         try:
    #             data_stream = io.BytesIO(request.data)
    #             self.minio_client.put_object(
    #                 self.bucket_name, resource_id, data_stream, len(request.data)
    #             )
    #         except S3Error as e:
    #             current_app.logger.error(f"Unable to upload object to MinIO: {e}")
    #             response.status_code = 500
    #             return response

    #         response.status_code = 201
    #         response.headers["Location"] = (
    #             f"{request.url_root}/{self.upload_url}/{resource_id}"
    #         )
    #         response.headers["Tus-Temp-Objectname"] = resource_id
    #         response.autocorrect_location_header = False

    #     else:
    #         current_app.logger.warning(
    #             "Received object upload for unsupported object transfer protocol"
    #         )
    #         response.data = (
    #             "Received object upload for unsupported object transfer protocol"
    #         )
    #         response.status_code = 500

    #     return response

    def tus_object_upload(self):
        """Handle TUS protocol for object upload operations."""
        response = make_response("", 200)

        if request.method == "HEAD":
            return self.handle_head_request(response)

        if request.method == "GET":
            return self.handle_get_request(response)

        if request.method == "OPTIONS" and request.headers.get(
            "Access-Control-Request-Method"
        ):
            response.headers["Tus-Resumable"] = self.tus_api_version
            response.headers["Tus-Version"] = self.tus_api_version_supported
            response.headers["Tus-Extension"] = ",".join(self.tus_api_extensions)
            response.headers["Tus-Max-Size"] = self.tus_max_object_size
            response.status_code = 204
            return response

        if request.headers.get("Tus-Resumable"):
            response.headers["Tus-Resumable"] = self.tus_api_version
            response.headers["Tus-Version"] = self.tus_api_version_supported

            if request.method in ["POST", "PUT"]:
                return self.handle_upload(response)

        current_app.logger.warning(
            "Received unsupported protocol or method for object upload"
        )
        response.data = "Unsupported protocol or method"
        response.status_code = 500
        return response

    def handle_upload(self, response):
        """Handle file upload for POST/PUT requests."""
        metadata = {}
        upload_metadata = request.headers.get("Upload-Metadata", None)
        if upload_metadata:
            for kv in upload_metadata.split(","):
                key, value = kv.split(" ")
                metadata[key] = base64.b64decode(value).decode("utf-8")

        if not self.object_overwrite:
            try:
                incoming_sha256 = self.compute_sha256(request.data)

                for obj in self.minio_client.list_objects(
                    self.bucket_name, recursive=True
                ):
                    existing_data = self.minio_client.get_object(
                        self.bucket_name, obj.object_name
                    )
                    existing_sha256 = self.compute_sha256(existing_data.read())
                    existing_data.close()

                    if existing_sha256 == incoming_sha256:
                        response.status_code = 409
                        response.data = json.dumps(
                            {
                                "message": (
                                    "Object with the same content already exists."
                                ),
                                "objectname": obj.object_name,
                            }
                        )
                        response.headers["Content-Type"] = "application/json"
                        return response

            except S3Error as e:
                if e.code != "NoSuchKey":
                    response.status_code = 500
                    return response

        resource_id = str(uuid.uuid4())

        try:
            data_stream = io.BytesIO(request.data)
            self.minio_client.put_object(
                self.bucket_name, resource_id, data_stream, len(request.data)
            )
        except S3Error as e:
            current_app.logger.error(f"Unable to upload object to MinIO: {e}")
            response.status_code = 500
            return response

        response.status_code = 201
        response.headers["Location"] = (
            f"{request.url_root}/{self.upload_url}/{resource_id}"
        )
        response.headers["Tus-Temp-Objectname"] = resource_id
        response.autocorrect_location_header = False

        return response

    def handle_head_request(self, response):
        """Handle the HEAD request for retrieving object status or upload offset.

        Args:
            response (Response): The response object to be returned.

        Returns:
            Response: The modified response object with object status or offset.
        """
        resource_id = request.headers.get("Resource-ID")
        if not resource_id:
            response.status_code = 400
            response.data = "Resource-ID header missing"
            return response

        try:
            obj_stat = self.minio_client.stat_object(self.bucket_name, resource_id)
            response.headers["Upload-Offset"] = obj_stat.size
            response.headers["Tus-Resumable"] = self.tus_api_version
            response.status_code = 200
        except S3Error as e:
            if e.code == "NoSuchKey":
                response.status_code = 404
            else:
                response.status_code = 500
        return response

    def handle_get_request(self, response):
        """Handle the GET request for fetching metadata or object existence status.

        Args:
            response (Response): The response object to be returned.

        Returns:
            Response: The modified response object with metadata or object status.
        """
        metadata = {}
        upload_metadata = request.headers.get("Upload-Metadata", None)
        if upload_metadata:
            for kv in upload_metadata.split(","):
                key, value = kv.split(" ")
                metadata[key] = base64.b64decode(value).decode("utf-8")

        if metadata.get("objectname") is None:
            return make_response("Metadata objectname is not set", 404)

        try:
            self.minio_client.get_object(self.bucket_name, metadata["objectname"])
            response.headers["Tus-Object-Name"] = metadata["objectname"]
            response.headers["Tus-Object-Exists"] = True
        except S3Error as e:
            if e.code == "NoSuchKey":
                response.headers["Tus-Object-Exists"] = False
            else:
                response.status_code = 500
                return response
        return response

    def tus_object_upload_chunk(self, resource_id):
        """Handle TUS protocol chunk upload operations for a given resource.

        Supports HTTP methods:
            - HEAD: Get the current upload offset.
            - DELETE: Delete the uploaded object.
            - PATCH: Append a chunk of data to the existing object.

        Args:
            resource_id (str): Unique identifier for the resource being uploaded.

        Returns:
            Flask response: Response indicating success or error.
        """
        response = make_response("", 204)
        response.headers["Tus-Resumable"] = self.tus_api_version
        response.headers["Tus-Version"] = self.tus_api_version_supported

        try:
            if request.method == "HEAD":
                # Handle HEAD request for chunk offset
                existing_data = self.minio_client.get_object(
                    self.bucket_name, resource_id
                )
                object_info = existing_data.read()
                response.headers["Upload-Offset"] = len(object_info)
                existing_data.close()
                response.status_code = 200
                response.headers["Cache-Control"] = "no-store"
                return response

            if request.method == "DELETE":
                # Handle DELETE request to remove object
                self.minio_client.remove_object(self.bucket_name, resource_id)
                response.status_code = 204
                return response

            if request.method == "PATCH":
                # Handle PATCH request to upload a chunk
                new_data = request.data
                current_size = 0

                try:
                    existing_data = self.minio_client.get_object(
                        self.bucket_name, resource_id
                    )
                    existing_data_bytes = existing_data.read()
                    current_size = len(existing_data_bytes)
                    new_data = existing_data_bytes + new_data
                except S3Error as e:
                    if e.code != "NoSuchKey":
                        raise

                data_stream = io.BytesIO(new_data)
                self.minio_client.put_object(
                    self.bucket_name, resource_id, data_stream, len(new_data)
                )

                new_offset = current_size + len(request.data)
                response.headers["Upload-Offset"] = new_offset
                response.status_code = 204
                response.headers["Cache-Control"] = "no-store"
                return response

        except S3Error as e:
            if e.code == "NoSuchKey":
                response.status_code = 404
                logging.error(f"Object not found: {resource_id}")
            else:
                response.status_code = 500
                logging.error(f"Error: {e}")

        return response
