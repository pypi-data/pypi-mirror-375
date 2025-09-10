from urllib.parse import urlparse


def _uri_validator(x: str) -> bool:
    """Validate that a string is a valid URI."""
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
