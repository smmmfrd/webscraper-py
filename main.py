import sys
import requests
import asyncio
import aiohttp

from urllib import parse
from crawl import PageData, normalize_url, extract_page_data

class AsyncCrawler:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.base_domain = parse.urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = 3
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AsyncCrawler":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.page_data:
                return False
            else:
                return True

    async def get_html(self, url: str) -> str | None:
        if self.session is None:
            return None
        try:
            async with self.session.get(
                url, headers={"User-Agent": "PyCrawler/1.0"}
            ) as r:
                if r.status > 399:
                    print(f"Error: {r.status}; {r.reason}")
                    return None

                content_type = r.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"Error: no html found {content_type}")
                    return None

                return await r.text()

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None


    async def crawl_page(self, current_url: str) -> None:
        # Check domains match first
        if parse.urlsplit(self.base_url).netloc != parse.urlsplit(current_url).netloc:
            return

        normalized_current = normalize_url(current_url)

        if normalized_current in self.page_data:
            return

        async with self.semaphore:
            print(f"crawling {current_url}")
            html = await self.get_html(current_url)
            if html is None:
                return
            
            data = extract_page_data(html, self.base_url)
            async with self.lock:
                self.page_data[normalized_current] = data

            next_urls = data.get('outgoing_links')

        tasks: list[asyncio.Task[None]] = []

        for next_url in next_urls:
            tasks.append(asyncio.create_task(self.crawl_page(next_url)))

        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url: str) -> dict[str, PageData]:
    async with AsyncCrawler(base_url) as crawler:
        return await crawler.crawl()

async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)

    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = sys.argv[1]
    data = await crawl_site_async(base_url)
    print(f"Found {len(data)} pages.")

    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
