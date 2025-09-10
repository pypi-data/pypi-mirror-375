import os
import logging

logger = logging.getLogger(__name__)


def list_object_count_and_bytes_gs(bucket_name):
    """list gcs bucket objects size and count

    1. `pip install google-cloud-storage`
    2. `GOOGLE_APPLICATION_CREDENTIALS` must be set

    Args:
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import time
    from google.cloud import storage

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    total_bytes = 0
    total_count = 0
    for blob in bucket.list_blobs():
        total_bytes += blob.size
        total_count += 1

    return {"bytes": total_bytes, "count": total_count}


def list_object_count_and_bytes_az(bucket_name):
    """list azure blob storage objects size and count

    1. `pip install azure-storage-blob`
    2. `AZURE_STORAGE_CONNECTION_STRING` must be set

    Args:
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import os
    from azure.storage.blob import BlobServiceClient

    blob_service_client = BlobServiceClient.from_connection_string(
        os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    )

    container_client = blob_service_client.get_container_client(bucket_name)

    total_size = 0
    total_count = 0
    for blob in container_client.list_blobs():
        total_size += blob.size
        total_count += 1

    return {"bytes": total_size, "count": total_count}


def list_object_count_and_bytes_s3(bucket_name):
    """list s3 bucket objects size and count

    1. `pip install boto3`
    2.  `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` must be set

    Args:
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import boto3

    s3 = boto3.resource("s3")

    bucket = s3.Bucket(bucket_name)

    total_size = 0
    total_count = 0
    for obj in bucket.objects.all():
        total_size += obj.size
        total_count += 1

    return {"bytes": total_size, "count": total_count}


def list_object_count_and_bytes_oss(bucket_name):
    """list oss bucket objects size and count

    1. `pip install oss2`
    2. `OSS_ACCESS_KEY_ID`, `OSS_ACCESS_KEY_SECRET` must be set

    Args:
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import oss2

    auth = oss2.Auth(
        os.environ["OSS_ACCESS_KEY_ID"], os.environ["OSS_ACCESS_KEY_SECRET"]
    )
    bucket = oss2.Bucket(auth, os.environ['OSS_ENDPOINT'] or "oss-cn-hangzhou.aliyuncs.com", bucket_name)

    total_size = 0
    total_count = 0
    for obj in oss2.ObjectIterator(bucket):
        total_size += obj.size
        total_count += 1

    return {"bytes": total_size, "count": total_count}


def list_object_count_and_bytes_minio(bucket_name):
    """list minio bucket objects size and count

    1. `pip install minio`
    2. `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` must be set

    Args:
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import os
    import minio

    client = minio.Minio(
        os.environ["MINIO_ENDPOINT"],
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=False,
    )

    total_size = 0
    total_count = 0
    for obj in client.list_objects(bucket_name, recursive=True):
        total_size += obj.size
        total_count += 1

    return {"bytes": total_size, "count": total_count}


def list_object_count_and_bytes_rclone_by_env(bucket_uri):
    """
    https://rclone.org/docs/#environment-variables
    """
    import subprocess
    import json
    import os
    from urllib.parse import urlparse

    def parse_path_uri(storage_bucket):
        parsed_url = urlparse(storage_bucket)
        scheme = parsed_url.scheme
        bucket_name = parsed_url.netloc
        blob_path = parsed_url.path.lstrip("/")
        return scheme, bucket_name, blob_path

    def check_rclone_installed():
        command = ["/opt/homebrew/bin/rclone", "version"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.returncode == 0

    is_rclone_installed = check_rclone_installed()
    logger.info("is_rclone_installed: %s", is_rclone_installed)
    if not is_rclone_installed:
        return None

    scheme, bucket_name, blob_path = parse_path_uri(bucket_uri)
    env = {}
    if scheme == "gs" or scheme == "gcs":
        env = {
            "RCLONE_CONFIG_MYREMOTE_TYPE": "google cloud storage",
            "RCLONE_CONFIG_MYREMOTE_SERVICE_ACCOUNT_FILE": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_SERVICE_ACCOUNT_FILE", None
            ),
            "RCLONE_CONFIG_MYREMOTE_PROJECT_NUMBER": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_PROJECT_NUMBER", None
            ),
            "RCLONE_CONFIG_MYREMOTE_LOCATION": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_LOCATION", "us-central1"
            ),
            "RCLONE_CONFIG_MYREMOTE_OBJECT_ACL": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_OBJECT_ACL", "private"
            ),
            "RCLONE_CONFIG_MYREMOTE_BUCKET_ACL": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_BUCKET_ACL", "private"
            ),
        }
    elif scheme == "s3":
        env = {
            "RCLONE_CONFIG_MYREMOTE_TYPE": "s3",
            "RCLONE_CONFIG_MYREMOTE_PROVIDER": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_PROVIDER", "AWS"
            ),
            "RCLONE_CONFIG_MYREMOTE_ACCESS_KEY_ID": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ACCESS_KEY_ID", None
            ),
            "RCLONE_CONFIG_MYREMOTE_SECRET_ACCESS_KEY": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_SECRET_ACCESS_KEY", None
            ),
            "RCLONE_CONFIG_MYREMOTE_REGION": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_REGION", "us-east-1"
            ),
            "RCLONE_CONFIG_MYREMOTE_ACL": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ACL", "private"
            ),
        }
    elif scheme == "azure" or scheme == "az":
        env = {
            "RCLONE_CONFIG_MYREMOTE_TYPE": "azureblob",
            "RCLONE_CONFIG_MYREMOTE_ACCOUNT": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ACCOUNT", None
            ),
            "RCLONE_CONFIG_MYREMOTE_KEY": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_KEY", None
            ),
        }
    elif scheme == "oss":
        env = {
            "RCLONE_CONFIG_MYREMOTE_TYPE": "s3",
            "RCLONE_CONFIG_MYREMOTE_PROVIDER": "Alibaba",
            "RCLONE_CONFIG_MYREMOTE_ACCESS_KEY_ID": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ACCESS_KEY_ID", None
            ),
            "RCLONE_CONFIG_MYREMOTE_SECRET_ACCESS_KEY": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_SECRET_ACCESS_KEY", None
            ),
            "RCLONE_CONFIG_MYREMOTE_ENDPOINT": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ENDPOINT", "oss-cn-hongkong.aliyuncs.com"
            ),
            "RCLONE_CONFIG_MYREMOTE_ACL": os.environ.get(
                "RCLONE_CONFIG_MYREMOTE_ACL", "private"
            ),
        }

    command = ["/opt/homebrew/bin/rclone", "--config", "/Users/caiying/.config/rclone/rclone.conf", "size", f"myremote:{bucket_name}", "--fast-list", "--json"]
    result = subprocess.run(command, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        logger.error("rclone command failed: %s", result.stderr)
        return None

    size_info = json.loads(result.stdout)
    return size_info


def list_object_count_and_bytes_rclone_by_conn_str(bucket_uri, conn_str):
    """list bucket objects size and count by rclone connection string

    https://rclone.org/docs/#hongkongconnection-strings
    """
    import subprocess
    import json
    from urllib.parse import urlparse

    def parse_path_uri(storage_bucket):
        parsed_url = urlparse(storage_bucket)
        scheme = parsed_url.scheme
        bucket_name = parsed_url.netloc
        blob_path = parsed_url.path.lstrip("/")
        return scheme, bucket_name, blob_path

    def check_rclone_installed():
        command = ["/opt/homebrew/bin/rclone", "version"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.returncode == 0

    is_rclone_installed = check_rclone_installed()
    if not is_rclone_installed:
        return None

    scheme, bucket_name, blob_path = parse_path_uri(bucket_uri)

    command = ["/opt/homebrew/bin/rclone", "--config", "/Users/caiying/.config/rclone/rclone.conf", "size", f"{conn_str}{bucket_name}", "--fast-list", "--json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    if result.returncode != 0:
        logger.error("rclone command failed: %s", result.stderr)
        return None

    size_info = json.loads(result.stdout)
    return size_info


def list_object_count_and_bytes_rclone_by_config(bucket_uri, config):
    """list bucket objects size and count by rclone config

    google cloud storage example:
    {
        "type": "google cloud storage",
        "service_account_file": "/path/to/service_account.json",
        "project_number": "<project-number>",
        "location": "us-central1",
        "object_acl": "private",
        "bucket_acl": "private",
    }

    aws s3 example:
    {
        "type": "s3",
        "provider": "AWS",
        "access_key_id": "<access-key-id>",
        "secret_access_key": "<secret-access-key>",
        "region": "us-east-1",
        "acl": "private",
    }

    azure blob storage example:
    {
        "type": "azureblob",
        "account": "<account-name>",
        "key": "<account-key>",
    }

    alibaba cloud oss example:
    {
        "type": "s3",
        "provider": "Alibaba",
        "access_key_id": "<access-key-id>",
        "secret_access_key": "<secret-access-key>",
        "endpoint": "oss-cn-shanghai.aliyuncs.com",
        "acl": "private",
    }
    """

    def create_rclone_connection_string(config):
        conn_type = config.pop("type", None)
        if conn_type is None:
            logger.error("The 'type' key is required in the configuration.")
            return None

        parts = [f"{key}={value}" for key, value in config.items()]
        connection_string = f":{conn_type}," + ",".join(parts) + ":"
        return connection_string

    if config is None:
        logger.error("The 'config' argument is required in the configuration.")
        return None

    conn_str = create_rclone_connection_string(config)

    list_object_count_and_bytes_rclone_by_conn_str(bucket_uri, conn_str)
