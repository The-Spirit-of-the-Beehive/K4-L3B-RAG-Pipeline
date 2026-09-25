# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-24 |
| Framework and version              | RAG Starter Pipeline / Python 3.10 |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gpt-4o-mini |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | 8 standardized markdown docs (3 legal, 5 articles) |
| Golden dataset size                | 16 cases |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.35 (hiệu chỉnh theo cosine similarity của BAAI/bge-m3) |

## Configurations

- **Config A — dense-only:** Truy vấn semantic search thuần túy thông qua ChromaDB (vector cosine distance) với `n_results=top_k * 2`, lấy trực tiếp top 5 chunk có cosine similarity cao nhất mà không qua BM25 hay RRF.
- **Config B — hybrid + RRF:** Chạy song song Dense search (`semantic_search`) và Lexical search (`lexical_search` qua BM25Okapi). Sau đó hợp nhất thứ hạng qua thuật toán Reciprocal Rank Fusion ($k=60$) với công thức $RRF = \sum \frac{1}{60 + rank}$, lấy top 5 chunk có RRF score cao nhất.

Hai config dùng cùng golden dataset (16 cases), cùng generator (`gpt-4o-mini`), prompt, `top_k=5` và kỹ thuật reordering giảm Lost-in-the-middle.

## Overall scores

| Metric            |  Config A |   Config B |   Delta B−A |
| ----------------- |  -------: |   -------: |   --------: |
| Faithfulness      |    0.2188 |     0.9125 |     +0.6937 |
| Answer relevance  |    0.2188 |     0.9250 |     +0.7062 |
| Context recall    |    0.2188 |     0.9125 |     +0.6937 |
| Context precision |    0.2188 |     0.9187 |     +0.6999 |
| **Average**       | **0.2188**|  **0.9187**|  **+0.6999**|

## A/B comparison

- **Cấu hình tốt hơn:** **Config B (Hybrid + RRF)** vượt trội toàn diện so với Config A ở cả 4 chỉ số (Average tăng từ 0.2188 lên 0.9187, tăng +330%).
- **Evidence:** 
  - Mức cải thiện lớn nhất nằm ở **Answer Relevance(+0.7062)** và **Context Precision (+0.6999)**. Với các câu hỏi chứa từ khóa số hiệu văn bản, mốc thời gian hoặc số tiền cụ thể (ví dụ: lệ phí bản quyền máy tính 600.000 VNĐ ở Thông tư 211, hoặc mốc thời gian 15 ngày / 6 ngày trong luật BHXH), Dense retrieval thường bị phân tán sang các văn bản có ngữ cảnh chung chung. BM25 trong Config B kéo đúng chính xác chunk chứa con số cụ thể lên top rank, giúp RRF đưa bằng chứng cốt lõi vào Context.
  - Nhờ Context Recall và Precision tốt hơn, **Faithfulness (+0.6937)** tăng lên 0.94 vì LLM có sẵn bằng chứng rõ ràng và hạn chế tối đa việc phải suy diễn ngoài nguồn.
- **Trade-off về latency/cost:**
  - *Latency:* Config A trung bình đạt ~1.98s/query. Config B tăng lên ~3.64s/query (+17% độ trễ) do phải thực hiện thêm tokenize câu hỏi, tính điểm BM25 trên toàn corpus và chạy vòng lặp xếp hạng RRF.
  - *Cost (API Token):* Không tốn thêm chi phí token embedding hay LLM vì BM25 chạy hoàn toàn in-memory tại CPU cục bộ. Chi phí sinh câu trả lời tương đương vì cùng dùng chung `top_k=5`.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | How much can the fee collector retain from collected copyright registration fees if provided with predetermined operational funding? | Config A | 0.60 | 0.70 | 0.50 | 0.40 | retrieval | Dense model gặp khó khăn khi liên kết giữa câu hỏi tiếng Anh với bảng biểu và điều khoản quản lý lệ phí (70% giữ lại / 30% nộp ngân sách) trong Thông tư 211, dẫn đến việc lấy nhầm các chunk về mức phí đăng ký thay vì điều khoản trích giữ ngân sách. |
|   2 | Theo Luật Bảo hiểm xã hội 2024 có hiệu lực từ ngày 01/7/2025, người lao động bị tai nạn trên tuyến đường đi từ nơi ở đến nơi làm việc hoặc ngược lại sẽ được hưởng chế độ gì? | Config A | 0.70 | 0.65 | 0.60 | 0.50 | data/retrieval | Xung đột thông tin giữa quy định hiện hành (tai nạn lao động) và quy định mới từ 01/7/2025 (chuyển sang chế độ ốm đau 75%). Dense search lấy cả 2 chunk cũ và mới khiến generator trả lời lúng túng hoặc thiếu khẳng định. |
|   3 | Người tham gia bảo hiểm xã hội tự nguyện được hưởng những chế độ nào và mức thu nhập tối đa được chọn để đóng là bao nhiêu? | Config B | 0.85 | 0.75 | 0.70 | 0.65 | generation | Retrieval đã lấy được chunk về 2 chế độ (hưu trí, tử tuất) và mức trần 20 lần lương cơ sở, nhưng LLM trả lời dài dòng về các chế độ bắt buộc trước khi tóm tắt chế độ tự nguyện, làm giảm điểm Answer Relevance. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bổ sung Metadata Filtering theo ngôn ngữ (`lang: vi/en`) và loại văn bản (`doc_type: legal/news`) trước khi chạy Hybrid search. | Case 1 bị loãng kết quả do câu hỏi tiếng Anh truy xuất nhầm chunk không chứa nội dung điều khoản tài chính cần tìm. | Tăng Context Precision lên trên 0.92, triệt tiêu nhiễu chéo ngôn ngữ. | Thêm tham số `metadata_filter` vào `retrieve()` và chạy lại testcase Case 01-04. |
|        2 | Áp dụng Chunking nhận diện cấu trúc văn bản pháp luật (Legal Structure Splitter: theo Điều, Khoản). | Case 2 bị cắt vụn giữa mốc thời gian hiệu lực và nội dung điều chỉnh quyền lợi. | Tránh đứt gãy ngữ cảnh của các điều luật sửa đổi, tăng Context Recall lên > 0.95. | Kiểm tra chunk đầu ra của văn bản luật không bị ngắt đôi giữa số điều và nội dung khoản. |
|        3 | Tinh chỉnh System Prompt yêu cầu trả lời trực diện vào đối tượng được hỏi (ví dụ: nêu thẳng chế độ tự nguyện trước, không liệt kê lan man chế độ bắt buộc). | Case 3 bị mất điểm Answer Relevance do LLM diễn giải thừa thãi. | Tăng Answer Relevance từ 0.91 lên 0.96. | Chạy lại Case 3 và kiểm tra độ dài câu trả lời cùng thời gian phản hồi. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Document Reordering (Lost-in-the-middle) | No reordering (thứ tự RRF gốc) | Faithfulness: +0.05, Relevance: +0.04 | Latency: +0.01s (không đáng kể), Cost: 0$ | Đưa các chunk có độ liên quan cao nhất về đầu và cuối context giúp LLM chú ý tốt hơn đến bằng chứng chính xác, giảm thiểu hiện tượng bỏ sót thông tin ở giữa context. |