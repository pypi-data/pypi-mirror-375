"""Base Package Utils."""

from urllib.parse import urlparse
from uuid import UUID


def is_uuid(uuid_str: str, version: int = 4) -> bool:
    """Validates if uuid_str is a valid uuid within a certain version.

    Args:
        uuid_str (str): uuid string.
        version (int, optional): uuid version of uuid_str.

    Returns:
        bool: whether uuid_str is a uuid or not.
    """
    try:
        uuid_obj = UUID(uuid_str, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str


def _validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_url(url: str) -> None:
    """Check if the url is valid."""
    if not _validate_url(url):
        msg = f"Invalid URL: {url}"
        raise ValueError(msg)
