import sys
import requests
# from bs4 import BeautifulSoup

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)

    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = sys.argv[1]
    print("starting crawl of: ", base_url)
    print(get_html(base_url))
    

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

if __name__ == "__main__":
    main()
