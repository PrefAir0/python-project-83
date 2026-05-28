from urllib.parse import urlparse
import validators


def is_valid(url):
    return validators.url(url) and len(url) <= 255


def normalize(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
