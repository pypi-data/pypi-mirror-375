from urllib.parse import urlparse
from ying.cloud_storage.list_object_count_and_bytes import (
    list_object_count_and_bytes_rclone_by_env,
    list_object_count_and_bytes_az,
    list_object_count_and_bytes_s3,
    list_object_count_and_bytes_oss,
    list_object_count_and_bytes_minio,
    list_object_count_and_bytes_gs,
)
from ying.cloud_storage.query_metrics import query_google_cloud_minitoring


def get_bucket_objects_count_and_bytes(bucket_uri, engine="auto", **kwargs):
    """get cloud storage bucket objects count and bytes

    Args:
        bucket_uri (cloud storage bucket uri):
            cloud storage bucket uri, e.g. "gs://bucket_name", "s3://bucket_name", "oss://bucket_name"
        engine (str, optional):
            cloud storage engine, ["auto", "rclone", "metrics", "sdk"]. Defaults to "rclone",
            metrics only support google cloud storage.

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    parsed_url = urlparse(bucket_uri)
    scheme = parsed_url.scheme
    bucket_name = parsed_url.netloc

    def process_by_metrics():
        if scheme != "gs":
            raise ValueError("metrics only support google cloud storage")
        if kwargs.get("project_id", None) is None:
            raise ValueError("project_id is required")
        project_id = kwargs.get("project_id")
        return query_google_cloud_minitoring(project_id, bucket_name)

    def process_by_rclone():
        return list_object_count_and_bytes_rclone_by_env(bucket_uri)

    def process_by_sdk():
        if scheme == "gs":
            return list_object_count_and_bytes_gs(bucket_uri)
        elif scheme == "s3":
            return list_object_count_and_bytes_s3(bucket_uri)
        elif scheme == "oss":
            return list_object_count_and_bytes_oss(bucket_uri)
        elif scheme == "minio":
            return list_object_count_and_bytes_minio(bucket_uri)
        elif scheme == "az":
            return list_object_count_and_bytes_az(bucket_uri)
        else:
            raise ValueError("unsupported scheme")

    return_value = None
    if engine == "auto":
        if scheme == "gs":
            return_value = process_by_metrics()

        if return_value is None:
            return_value = process_by_rclone()

        if return_value is None:
            return_value = process_by_sdk()
    elif engine == "metrics":
        return_value = process_by_metrics()
    elif engine == "rclone":
        return_value = process_by_rclone()
    elif engine == "sdk":
        return_value = process_by_sdk()
    return return_value
