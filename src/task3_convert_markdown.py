"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

import json
from pathlib import Path
from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    # TODO:Convert PDF/DOCX vào standardized/legal. 
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()
    for path in legal_dir.iterdir():
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            dest_file = output_dir / f"{path.stem}.md"
            print(f"Converting legal doc: {path.name} ...")

            result = converter.convert(str(path))
            text_content = result.text_content.strip()
            if not text_content:
                raise ValueError(f"Extracted content is empty for {path.name}")
            dest_file.write_text(text_content + "\n", encoding="utf-8")
            print(f"-> Saved: {dest_file} ({len(text_content):,} chars)")


def convert_news_articles() -> None:
    # TODO: Convert JSON vào standardized/news.
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in news_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        title = data.get("title", path.stem)
        url = data.get("url", "")
        date_crawled = data.get("date_crawled", "")
        body = data.get("content_markdown", "").strip()

        if not body:
            raise ValueError(f"Content is empty in {path.name}")

        header = (
            f"# {title}\n\n"
            f"- **Source:** {url}\n"
            f"- **Crawled:** {date_crawled}\n\n"
            f"---\n\n"
        )
        dest_file = output_dir / f"{path.stem}.md"
        dest_file.write_text(header + body + "\n", encoding="utf-8")
        print(f"-> Saved: {dest_file} ({len(body):,} chars)")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
