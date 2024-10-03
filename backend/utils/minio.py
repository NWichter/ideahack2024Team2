from secrets import MINIO_ACCESS_KEY, MINIO_SECRET_KEY

from minio import Minio

# Initialize MinIO client
minio_client = Minio(
    "minio:9000", access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False
)
