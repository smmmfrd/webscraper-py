import sys
import requests
from urllib import parse
from crawl import PageData, normalize_url, extract_page_data

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)

    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = sys.argv[1]
    data = crawl_page(base_url, base_url, {})
    print(f"Found {len(data)} pages.")


def crawl_page(base_url: str, current_url: str, page_data: dict[str, PageData]) -> dict[str, PageData]:
    # Check domains match first
    if parse.urlsplit(base_url).netloc != parse.urlsplit(current_url).netloc:
        return page_data

    normalized_current = normalize_url(current_url)

    if normalized_current in page_data:
        return page_data

    print(f"crawling {current_url}")
    html = safe_get_html(current_url)
    if html is None:
        return page_data
    data = extract_page_data(html, base_url)
    page_data[normalized_current] = data

    for url in data.get('outgoing_links'):
        page_data = crawl_page(base_url, url, page_data)

    return page_data

def get_html(url: str) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": "PyCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")


    if r.status_code > 399:
        raise Exception(f"HTML Error: {r.status_code} {r.reason}")

    content_type = r.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise Exception(f"No html found at {url}: {content_type}")

    return r.text

def safe_get_html(url: str) -> str | None:
    try:
        return get_html(url)
    except Exception as e:
        print(f"{e}")
        return None

if __name__ == "__main__":
    main()
