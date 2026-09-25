# Individual contribution report

## Thông tin

- Họ và tên: Đỗ Hoàng Quân
- Mã học viên: 2A202603016
- Nhóm: Cá nhân - Solo
- Repository/branch: K4-L3B-RAG-Pipeline / main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data Collection (Task 1 & 2) | Thu thập 3 tài liệu pháp lý thật (.pdf) và crawl 5 bài viết chính sách BHXH (.json) qua Crawl4AI. | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py` | Done |
| Markdown Standardization (Task 3) | Chuẩn hóa PDF và JSON sang định dạng Markdown có header metadata vào `data/standardized/`. | `src/task3_convert_markdown.py` | Done |
| Chunking & Indexing (Task 4) | Xây dựng pipeline cắt nhỏ văn bản (recursive), sinh embedding (BGE-M3/OpenAI) và upsert vào ChromaDB. | `src/task4_chunking_indexing.py` | Done |
| Dual Retrieval (Task 5 & 6) | Xây dựng Dense search qua Chroma cosine distance và Lexical search qua BM25Okapi trên cùng corpus chunk. | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| Reranking & Pipeline (Task 7 & 9) | Cài đặt thuật toán Reciprocal Rank Fusion (RRF), cơ chế fallback an toàn dựa trên cosine score gốc. | `src/task7_reranking.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation & Evaluation (Task 10 & Eval) | Thiết lập prompt citation `[Document X]`, reorder chống lost-in-the-middle, tạo 16 golden cases và hoàn thành benchmark A/B. | `src/task10_generation_citation.py`, `RESULT.md`, `golden_dataset.json` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Khắc phục lỗi IDF = 0 của thư viện `rank_bm25` khi corpus nhỏ bằng cách gán sàn giá trị dương tối thiểu (`0.5`) cho các từ khóa có $IDF \le 0$.  
   **Lý do/evidence:** Khi chạy contract test với corpus giả lập chỉ gồm 2 document, từ khóa xuất hiện ở 1 document có $IDF = \ln(1.0) = 0.0$. Dẫn đến điểm BM25 bằng 0 và bị hàm search lọc bỏ toàn bộ (`output = []`), gây lỗi `IndexError`.  
   **Trade-off:** Điểm BM25 của các từ phổ biến trong corpus nhỏ sẽ không phân tách quá sắc nét, nhưng bảo đảm pipeline không bao giờ bỏ sót kết quả khớp từ khóa chính xác và pass 100% test contract.

2. **Quyết định:** Tách biệt tuyệt đối giữa điểm xếp hạng RRF ($RRF = \sum \frac{1}{60 + rank}$) và điểm Cosine Similarity gốc khi kích hoạt Fallback. Đồng thời sử dụng `copy.deepcopy` khi thực hiện fusion.  
   **Lý do/evidence:** Hợp đồng module cấm sử dụng RRF score để so sánh với `SCORE_THRESHOLD` do hai thang đo khác nhau hoàn toàn về bản chất toán học. Việc deep copy ngăn chặn việc ghi đè trực tiếp lên danh sách gốc, giúp kiểm thử contract phân biệt được tính bất biến của dữ liệu.  
   **Trade-off:** Tốn thêm một lượng nhỏ bộ nhớ RAM và CPU time để clone danh sách dictionary, nhưng đảm bảo độ tin cậy và an toàn cho toàn bộ luồng xử lý phía sau.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_acceptance.py -q` và `pytest tests/test_contracts.py -q`.
- Kết quả trước/sau nếu có: 
  - Trước khi sửa BM25: 14 passed, 1 failed (`test_lexical_search_returns_bm25_contract`).
  - Sau khi sửa: 15/15 contract tests passed và toàn bộ acceptance tests passed.
- Lỗi đã phát hiện và cách xử lý: Lỗi `IndexError` ở Task 6 do BM25 loại bỏ chunk có điểm 0; xử lý bằng cách chuẩn hóa IDF sàn dương và truyền đúng biến `corpus`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Pipeline hiện tại chưa tích hợp reranker học sâu chuyên dụng (như BGE-Reranker hoặc Cohere API) mà chỉ dựa trên heuristic rank của RRF, dẫn đến việc chưa tái cân bằng tối ưu được trọng số giữa dense và lexical trong các câu hỏi đa ngữ (Anh - Việt).
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai Cross-Encoder Reranker để rerank lại top 20 kết quả từ RRF trước khi đưa vào LLM Context nhằm nâng cao hơn nữa chỉ số Context Precision.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-24
- Tên thành viên: Đỗ Hoàng Quân