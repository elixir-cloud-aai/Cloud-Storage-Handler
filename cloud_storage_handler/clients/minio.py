from cloud_storage_handler.clients.minio_client import MinioClient

def get_minio_client():
    client = MinioClient()
    client.create_bucket()
    return client