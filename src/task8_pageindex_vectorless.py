"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY chưa được cấu hình. Bỏ qua upload PageIndex.")
        return

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    try:
        import requests

        headers = {"Authorization": f"Bearer {PAGEINDEX_API_KEY}"}

        for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
            rel_path = path.relative_to(STANDARDIZED_DIR).as_posix()
            if rel_path in cache:
                continue

            with open(path, "rb") as f:
                response = requests.post(
                    "https://api.pageindex.ai/v1/documents",
                    headers=headers,
                    files={"file": (path.name, f, "text/markdown")},
                    timeout=30,
                )

            if response.status_code in (200, 201):
                data = response.json()
                doc_id = data.get("id") or data.get("document_id")
                if doc_id:
                    cache[rel_path] = doc_id
                    print(f"Uploaded {rel_path} -> {doc_id}")

        CACHE_FILE.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        print(f"Lỗi khi upload lên PageIndex: {e}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult theo schema của MODULE_CONTRACTS."""
    if not query or not query.strip() or not PAGEINDEX_API_KEY:
        return []

    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    doc_ids = list(cache.values())
    if not doc_ids:
        return []

    try:
        import requests

        headers = {
            "Authorization": f"Bearer {PAGEINDEX_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "top_k": top_k,
            "document_ids": doc_ids,
        }
        response = requests.post(
            "https://api.pageindex.ai/v1/search",
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code != 200:
            return []

        data = response.json()
        raw_items = data.get("results") or data.get("nodes") or []
        results = []

        for rank, item in enumerate(raw_items, 1):
            item_id = item.get("id", f"pageindex::{rank}")
            content = item.get("content") or item.get("text", "")
            # Nếu API không trả score, gán score giảm dần theo rank: 1 / rank
            score = float(item.get("score", 1.0 / rank))
            metadata = item.get("metadata", {})

            results.append({
                "id": str(item_id),
                "content": str(content),
                "score": score,
                "metadata": metadata if isinstance(metadata, dict) else {},
                "retrieval_method": "pageindex",
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    except Exception as e:
        print(f"PageIndex search error (safe fallback): {e}")
        return []


if __name__ == "__main__":
    upload_documents()
