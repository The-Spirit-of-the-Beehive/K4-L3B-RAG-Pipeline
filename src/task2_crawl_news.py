"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
from datetime import datetime
import json
from pathlib import Path
from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # TODO: Thêm ít nhất 5 public URL.
    "https://luatvietnam.vn/bao-hiem/cac-che-do-bhxh-tu-ngay-01-7-2025-thay-doi-nhu-the-nao-563-102823-article.html",
    "https://luatvietnam.vn/bao-hiem/dieu-kien-huong-bao-hiem-xa-hoi-1-lan-563-23984-article.html",
    "https://luatvietnam.vn/bao-hiem/muc-huong-che-do-thai-san-563-23795-article.html",
    "https://luatvietnam.vn/bao-hiem/dong-bao-hiem-xa-hoi-co-loi-ich-gi-563-93260-article.html#google_vignette",
    "https://luatvietnam.vn/bao-hiem/dieu-kien-huong-che-do-om-dau-563-23213-article.html",
]


async def crawl_article(url: str) -> dict:
    # TODO: Implement crawling logic.
    #
    # from datetime import datetime
    # from crawl4ai import AsyncWebCrawler
    #
    # async with AsyncWebCrawler() as crawler:
    #     result = await crawler.arun(url=url)
    #     return {
    #         "url": url,
    #         "title": result.metadata.get("title", "Unknown"),
    #         "date_crawled": datetime.now().isoformat(),
    #         "content_markdown": result.markdown,
    #     }
    """Crawl nội dung thực tế qua Crawl4AI và Playwright."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not result.success:
            raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

        title = result.metadata.get("title") if result.metadata else None
        if not title:
            title = url.rstrip("/").split("/")[-1]

        content_markdown = result.markdown or ""
        if not content_markdown.strip():
            raise ValueError(f"No markdown content extracted from {url}")

        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content_markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        output = DATA_DIR / f"article_{index:02d}.json"
        print(f"Crawling ({index}/{len(ARTICLE_URLS)}): {url}")
        
        # Gọi hàm crawl thật, nếu lỗi sẽ văng exception để xử lý đúng lỗi
        article = await crawl_article(url)
        output.write_text(
            json.dumps(article, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"-> Saved: {output} (Size: {len(article['content_markdown']):,} chars)")


if __name__ == "__main__":
    asyncio.run(crawl_all())
