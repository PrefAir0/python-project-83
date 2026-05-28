from urllib.parse import urlparse
import validators

def normalize(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def is_valid(url):
    return validators.url(url)