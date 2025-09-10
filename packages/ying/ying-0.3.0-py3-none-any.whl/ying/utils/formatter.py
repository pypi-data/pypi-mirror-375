import logging

logger = logging.getLogger(__name__)

def human_readable_bytes(size, decimal_places=2):
    if size < 0:
        logger.warning("Size should be a non-negative number")
        return str(size)

    if not isinstance(decimal_places, int) or decimal_places < 0:
        raise ValueError("decimal_places should be a non-negative integer")

    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    if size == 0:
        return f"0 {units[0]}"

    for unit in units:
        if size < 1024.0:
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit}"
