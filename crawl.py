from urllib import parse
from bs4 import BeautifulSoup, Tag

def normalize_url(url: str) -> str:
    parsed_url = parse.urlsplit(url)
    full_url = f"{parsed_url.netloc}{parsed_url.path}"
    full_url = full_url.rstrip('/')
    return full_url.lower()


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find('h1') or soup.find('h2')
    return heading.get_text(strip=True) if isinstance(heading, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')

    paragraph = main.find('p') if isinstance(main, Tag) else soup.find('p')

    return paragraph.get_text(strip=True) if isinstance(paragraph, Tag) else ""