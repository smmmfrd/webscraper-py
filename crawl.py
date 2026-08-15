from urllib import parse

def normalize_url(url: str) -> str:
    parsed_url = parse.urlsplit(url)
    full_url = f"{parsed_url.netloc}{parsed_url.path}"
    full_url = full_url.rstrip('/')
    return full_url.lower()
