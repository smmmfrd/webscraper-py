from urllib import parse
from bs4 import BeautifulSoup, Tag
from typing import TypedDict


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

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

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')

    anchors = soup.find_all('a')
    links :list[str] = []
    for a in anchors:
        link = a.get("href") if isinstance(a, Tag) else ""
        if isinstance(link, str):
            if ":" not in link:
                link = base_url + link
            links.append(link)

    return links

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')

    imgs = soup.find_all('img')
    links :list[str] = []
    for i in imgs:
        link = i.get("src") if isinstance(i, Tag) else ""
        if isinstance(link, str):
            if ":" not in link:
                link = base_url + link
            links.append(link)
    
    return links

def extract_page_data(html: str, page_url: str) -> PageData:

    return {
        'url': page_url,
        'heading': get_heading_from_html(html),
        'first_paragraph': get_first_paragraph_from_html(html),
        'image_urls': get_images_from_html(html, page_url),
        'outgoing_links': get_urls_from_html(html, page_url)
    }