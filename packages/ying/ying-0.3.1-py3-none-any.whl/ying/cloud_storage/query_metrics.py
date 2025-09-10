import logging

logger = logging.getLogger(__name__)


def query_google_cloud_minitoring(project_id, bucket_name):
    """query gcs bucket objects size and count

    1. `pip install google-cloud-monitoring`
    2. `GOOGLE_APPLICATION_CREDENTIALS` must be set

    Args:
        project_id (string): project id
        bucket_name (string): bucket name

    Returns:
        dict: { "bytes": storage_bytes_value, "count": storage_count_value }
    """
    import time
    from google.cloud import monitoring_v3

    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - 1200), "nanos": nanos},
        }
    )
    # https://cloud.google.com/monitoring/custom-metrics/reading-metrics
    storage_bytes = client.list_time_series(
        request={
            "name": project_name,
            "filter": f'metric.type="storage.googleapis.com/storage/total_bytes" AND resource.labels.bucket_name="{bucket_name}"',
            "interval": interval,
        }
    )

    storage_count = client.list_time_series(
        request={
            "name": project_name,
            "filter": f'metric.type="storage.googleapis.com/storage/object_count" AND resource.labels.bucket_name="{bucket_name}"',
            "interval": interval,
        }
    )

    try:
        storage_bytes_value = storage_bytes.time_series[0].points[0].value.double_value
    except Exception as e:
        logger.error(
            f"[project_id: {project_id}, bucket_name: {bucket_name}] get storage_bytes_value failed: {e}"
        )
        storage_bytes_value = -1
    try:
        storage_count_value = storage_count.time_series[0].points[0].value.int64_value
    except Exception as e:
        logger.error(
            f"[project_id: {project_id}, bucket_name: {bucket_name}] get storage_count_value failed: {e}"
        )
        storage_count_value = -1
    return {"bytes": storage_bytes_value, "count": storage_count_value}
