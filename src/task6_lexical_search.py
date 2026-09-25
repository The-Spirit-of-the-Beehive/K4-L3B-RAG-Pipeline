"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from rank_bm25 import BM25Okapi
import numpy as np

CORPUS: list[dict] = []

def _ensure_corpus() -> list[dict]:
    """Nạp corpus nếu chưa có dữ liệu trong biến CORPUS."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import get_collection
            col = get_collection()
            data = col.get(include=["documents", "metadatas"])
            if data and data.get("ids"):
                CORPUS = [
                    {"id": item_id, "content": doc, "metadata": meta}
                    for item_id, doc, meta in zip(
                        data["ids"], data["documents"], data["metadatas"]
                    )
                ]
        except Exception:
            pass

    if not CORPUS:
        try:
            from .task4_chunking_indexing import load_documents, chunk_documents
            docs = load_documents()
            CORPUS = chunk_documents(docs)
        except Exception:
            pass

    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    # TODO: Tokenize và tạo BM25 index.
    tokenized = [item["content"].lower().split() for item in corpus]
    bm25 = BM25Okapi(tokenized)
    # Khắc phục bug của rank_bm25 khi corpus nhỏ (N=2, n=1 -> idf = ln(1.0) = 0.0)
    for word, val in bm25.idf.items():
        if val <= 0:
            bm25.idf[word] = 0.5
    return bm25


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    # TODO: Tính BM25 scores và map lại corpus.
    if not query or not query.strip():
        return []
    corpus = CORPUS if CORPUS else _ensure_corpus()
    if not corpus: return []
    
    bm25 = build_bm25_index(CORPUS)
    if bm25 is None: return []
    query_tokens = query.lower().split()
    if not query_tokens: return []

    scores = bm25.get_scores(query_tokens)
    indices = np.argsort(scores)[::-1][:top_k]
    results = []
    seen_ids = set()

    for index in indices:
        if scores[index] <= 0:
            continue
        item = CORPUS[index]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])

        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
