from typing import List, Optional
import os

import requests

from ying.config import settings


def resolve_endpoint() -> str:
    """Resolve the notification service endpoint.

    Precedence: env YING_NOTIFY_URL -> dynaconf settings -> default.
    """
    env_value = os.environ.get("YING_NOTIFY_URL")
    if env_value:
        return env_value

    for key in ("NOTIFY_URL", "notify_url", "notify.url"):
        try:
            value = settings.get(key)
            if value:
                return value
        except Exception:
            # Ignore missing keys or settings backend errors
            pass

    return "https://notify.caiying.me/"


def send_notification(
    title: str,
    body: str,
    urls: List[str],
    endpoint: Optional[str] = None,
    timeout_seconds: int = 10,
) -> requests.Response:
    """Send a notification to the configured endpoint.

    Raises requests.HTTPError if non-2xx status.
    """
    service_endpoint = endpoint or resolve_endpoint()
    payload = {
        "title": title or "",
        "body": body or "",
        "urls": urls,
    }
    response = requests.post(service_endpoint, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    return response


