from flask import jsonify, make_response, send_file, request, current_app
import io
import zipfile
import hashlib
import uuid
import base64
from minio import Minio
from minio.error import S3Error
import logging
import json
import os

from http import HTTPStatus


logger = logging.getLogger(__name__)

def home():
    """Endpoint to return a welcome message."""
    return jsonify(
        {"message": "Welcome to the Cloud Storage Handler server!"}
    ), HTTPStatus.OK

class TusController:
    def __init__(self, app):
        self.app=app
        self.minio_client = app.app.config.foca.custom.minio.client.client
        self.bucket_name = app.app.config.foca.custom.minio.bucket_name
        logging.info(self.minio_client)
        logging.info(self.bucket_name)
        self.tus_api_version = "1.0.0"
        self.tus_api_version_supported = "1.0.0"
        self.tus_api_extensions = ["creation", "expiration", "termination"]
        self.tus_max_file_size = 50 * 1024 * 1024 * 1024  # 50 GB
        self.file_overwrite = False
        self.upload_url = "elixircloud/csh/v1/file-upload"

    def compute_sha256(self, data):
        """Compute the SHA-256 checksum of the provided data."""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()

    def tus_file_upload(self):
        response = make_response("", 200)

        if request.method == 'HEAD':
            resource_id = request.headers.get("Resource-ID")
            if not resource_id:
                response.status_code = 400
                response.data = "Resource-ID header missing"
                return response

            try:
                obj_stat = self.minio_client.stat_object(self.bucket_name, resource_id)
                response.headers['Upload-Offset'] = obj_stat.size
                response.headers['Tus-Resumable'] = self.tus_api_version
                response.status_code = 200
            except S3Error as e:
                if e.code == "NoSuchKey":
                    response.status_code = 404
                else:
                    response.status_code = 500
            return response

        elif request.method == 'GET':
            metadata = {}
            upload_metadata = request.headers.get("Upload-Metadata", None)
            if upload_metadata:
                for kv in upload_metadata.split(","):
                    key, value = kv.split(" ")
                    metadata[key] = base64.b64decode(value).decode('utf-8')

            if metadata.get("filename", None) is None:
                return make_response("Metadata filename is not set", 404)

            try:
                self.minio_client.get_object(self.bucket_name, metadata["filename"])
                response.headers['Tus-File-Name'] = metadata["filename"]
                response.headers['Tus-File-Exists'] = True
            except S3Error as e:
                if e.code == "NoSuchKey":
                    response.headers['Tus-File-Exists'] = False
                else:
                    response.status_code = 500
                    return response

            return response

        elif request.method == 'OPTIONS' and request.headers.get('Access-Control-Request-Method', None) is not None:
            return response

        if request.headers.get("Tus-Resumable") is not None:
            response.headers['Tus-Resumable'] = self.tus_api_version
            response.headers['Tus-Version'] = self.tus_api_version_supported

            if request.method == 'OPTIONS':
                response.headers['Tus-Extension'] = ",".join(self.tus_api_extensions)
                response.headers['Tus-Max-Size'] = self.tus_max_file_size
                response.status_code = 204
                return response

            metadata = {}
            upload_metadata = request.headers.get("Upload-Metadata", None)
            if upload_metadata:
                for kv in upload_metadata.split(","):
                    key, value = kv.split(" ")
                    metadata[key] = base64.b64decode(value).decode('utf-8')

            if not self.file_overwrite:
                try:
                    incoming_sha256 = self.compute_sha256(request.data)

                    for obj in self.minio_client.list_objects(self.bucket_name, recursive=True):
                        existing_data = self.minio_client.get_object(self.bucket_name, obj.object_name)
                        existing_sha256 = self.compute_sha256(existing_data.read())
                        existing_data.close()

                        if existing_sha256 == incoming_sha256:
                            response.status_code = 409
                            response.data = json.dumps({
                                "message": "File with the same content already exists.",
                                "filename": obj.object_name
                            })
                            response.headers['Content-Type'] = 'application/json'
                            return response
                        
                except S3Error as e:
                    if e.code != "NoSuchKey":
                        response.status_code = 500
                        return response

            file_size = int(request.headers.get("Upload-Length", "0"))
            resource_id = str(uuid.uuid4())

            try:
                data_stream = io.BytesIO(request.data)
                self.minio_client.put_object(self.bucket_name, resource_id, data_stream, len(request.data))
            except S3Error as e:
                current_app.logger.error("Unable to upload file to MinIO: {}".format(e))
                response.status_code = 500
                return response

            response.status_code = 201
            response.headers['Location'] = '{}/{}/{}'.format(request.url_root, self.upload_url, resource_id)
            response.headers['Tus-Temp-Filename'] = resource_id
            response.autocorrect_location_header = False

        else:
            current_app.logger.warning("Received file upload for unsupported file transfer protocol")
            response.data = "Received file upload for unsupported file transfer protocol"
            response.status_code = 500

        return response

    def tus_file_upload_chunk(self, resource_id):
        response = make_response("", 204)
        response.headers['Tus-Resumable'] = self.tus_api_version
        response.headers['Tus-Version'] = self.tus_api_version_supported

        if request.method == 'HEAD':
            try:
                existing_data = self.minio_client.get_object(self.bucket_name, resource_id)
                file_info = existing_data.read()
                logging.info(len(file_info))
                response.headers['Upload-Offset'] = len(file_info)
                existing_data.close()
                response.status_code = 200
                response.headers['Cache-Control'] = 'no-store'
                return response
            except S3Error as e:
                if e.code == "NoSuchKey":
                    response.status_code = 404
                    logging.error("File not found: {}".format(resource_id))
                else:
                    response.status_code = 500
                    logging.error("Error fetching file info: {}".format(e))
                return response

        if request.method == 'DELETE':
            try:
                self.minio_client.remove_object(self.bucket_name, resource_id)
                response.status_code = 204
                return response
            except S3Error as e:
                current_app.logger.error("Error deleting file from MinIO: {}".format(e))
                response.status_code = 500
                response.data = "Unable to delete file"
                return response

        if request.method == 'PATCH':
            try:
                existing_file = False
                current_size = 0
                new_data = request.data

                try:
                    existing_data = self.minio_client.get_object(self.bucket_name, resource_id)
                    existing_file = True
                    existing_data_bytes = existing_data.read()
                    current_size = len(existing_data_bytes)
                    new_data = existing_data_bytes + new_data
                except S3Error as e:
                    if e.code == "NoSuchKey":
                        pass
                    else:
                        raise

                data_stream = io.BytesIO(new_data)
                self.minio_client.put_object(self.bucket_name, resource_id, data_stream, len(new_data))

                new_offset = current_size + len(request.data)
                response.headers['Upload-Offset'] = new_offset
                response.headers['Tus-Temp-Filename'] = resource_id

                if new_offset == int(request.headers.get("Upload-Length", "0")):
                    if self.upload_file_handler_cb is None:
                        current_app.logger.info("Upload completed: {}".format(resource_id))
                    else:
                        filename = self.upload_file_handler_cb(upload_file_path, resource_id)

                    if self.upload_finish_cb is not None:
                        self.upload_finish_cb()

                return response

            except S3Error as e:
                current_app.logger.error("Error during file upload to MinIO: {}".format(e))
                response.status_code = 500
                return response

    def tus_file_download(self, resource_id):
        """
        Retrieves and downloads a file from MinIO storage.
        
        :param resource_id: The unique identifier for the file to be downloaded
        :return: Flask response with the file content for download
        """
        try:
            file_obj = self.minio_client.get_object(self.bucket_name, resource_id)
        
            file_stream = io.BytesIO(file_obj.read())
            file_stream.seek(0)

            return send_file(
                file_stream,
                as_attachment=True,  
                download_name=f"{resource_id}.file",
                mimetype="application/octet-stream"
            )

        except S3Error as e:
            current_app.logger.error("Error downloading file from MinIO: {}".format(e))
            response = make_response("Unable to download file", 500)
            return response

    def list_files(self):
        """
        Lists all files in the MinIO bucket.
        
        :return: JSON response with a list of file names
        """
        try:
            files = [obj.object_name for obj in self.minio_client.list_objects(self.bucket_name, recursive=True)]
            return jsonify(files), 200
        except S3Error as e:
            current_app.logger.error("Error listing files in MinIO: {}".format(e))
            return jsonify({"error": "Unable to list files"}), 500

    def download_all_files(self):
        """
        Downloads all files from the MinIO bucket as a zip file.
        
        :return: Flask response with the zip file for download
        """
        try:

            zip_io = io.BytesIO()

            with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for obj in self.minio_client.list_objects(self.bucket_name):
                    file_data = self.minio_client.get_object(self.bucket_name, obj.object_name)
                    zip_file.writestr(obj.object_name, file_data.read())
                    file_data.close()

            zip_io.seek(0)
            return send_file(
                zip_io,
                as_attachment=True,
                download_name="all_files.zip",
                mimetype="application/zip"
            )
        except S3Error as e:
            current_app.logger.error("Error downloading files from MinIO: {}".format(e))
            return make_response("Unable to download files", 500)


