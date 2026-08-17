import sys
import asyncio
import aiohttp
from urllib import parse

from crawl import PageData, normalize_url, extract_page_data
from json_report import write_json_report

class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int, max_pages: int) -> None:
        self.base_url = base_url
        self.base_domain = parse.urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None

        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task[None]] = set()

    async def __aenter__(self) -> "AsyncCrawler":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url: str):
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.page_data:
                return False
            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("reached max pages to crawl")
                for task in self.all_tasks:
                    if not task.done():
                        task.cancel()
                return False
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
        if self.should_stop:
            return

        # Check domains match first
        if parse.urlsplit(self.base_url).netloc != parse.urlsplit(current_url).netloc:
            return

        normalized_current = normalize_url(current_url)

        is_new = await self.add_page_visit(normalized_current)
        if not is_new:
            return

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
            task = asyncio.create_task(self.crawl_page(next_url))
            tasks.append(task)
            self.all_tasks.add(task)

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int) -> dict[str, PageData]:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()

async def main():
    if len(sys.argv) < 4:
        print("too few arguments provided")
        sys.exit(1)

    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url, max_concurrency, max_pages = sys.argv[1], sys.argv[2], sys.argv[3]
    data = await crawl_site_async(base_url, int(max_concurrency), int(max_pages))

    write_json_report(data)

    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
