# THÔNG TIN THÀNH VIÊN VÀ PHÂN CÔNG DỰ ÁN
**Môn học:** AI Thực chiến (K4)  
**Bài Lab:** Lab 08 — Xây dựng và đánh giá RAG Pipeline  
**Nhóm:** Cá nhân - Solo  
**Chủ đề Corpus:** Chính sách & Quy định Bảo hiểm Xã hội (BHXH)  

---

## 1. Thông tin thành viên

| STT | Họ và tên | Mã học viên | Vai trò | Nhánh phụ trách |
| :---: | :--- | :---: | :--- | :--- |
| 1 | Đỗ Hoàng Quân | 2A202603016 | **Toàn quyền (End-to-End Pipeline)**<br>- Data Engineering<br>- Retrieval & Indexing<br>- Generation & Streamlit UI<br>- Evaluation & A/B Testing | `main` |

---

## 2. Chi tiết phân công công việc

Vì thực hiện độc lập, toàn bộ các Task trong quy trình Lab 08 do một thành viên đảm nhiệm:

1. **Phase 1 — Data & Corpus Preparation (Task 1, 2, 3):**
   - Thu thập tài liệu pháp lý (.pdf) vào `data/landing/legal/`.
   - Thu thập bài viết tin tức (.json) vào `data/landing/news/`.
   - Chuẩn hóa toàn bộ corpus sang Markdown vào `data/standardized/`.
   - Vượt qua bài kiểm tra `test_acceptance.py`.

2. **Phase 2 — Indexing & Retrieval Pipeline (Task 4):**
   - Xây dựng pipeline chunking tài liệu.
   - Cài đặt Dense Retrieval (Vector Embedding) và Sparse Retrieval (BM25).
   - Tích hợp thuật toán Reciprocal Rank Fusion (RRF) để kết hợp kết quả.

3. **Phase 3 — Generation & UI (Task 5):**
   - Tích hợp LLM sinh phản hồi bám sát ngữ cảnh kèm Citation (trích dẫn nguồn).
   - Xử lý kịch bản Fallback khi thiếu bằng chứng truy xuất.
   - Xây dựng giao diện Chatbot bằng Streamlit.

4. **Phase 4 — Evaluation & A/B Testing (Task 6):**
   - Thiết lập bộ câu hỏi Benchmark đánh giá retrieval.
   - So sánh định lượng giữa mô hình Dense-only và Hybrid + RRF.
   - Hoàn thiện báo cáo phân tích A/B testing.