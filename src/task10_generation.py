"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Bạn là trợ lý AI trả lời câu hỏi dựa trên các tài liệu được cung cấp.
Quy tắc bắt buộc:
1. Trả lời CHỈ dựa trên thông tin có trong phần Context dưới đây. Tuyệt đối không suy đoán hay thêm thông tin ngoài.
2. Mỗi khẳng định, số liệu hoặc quy định được nêu ra PHẢI có trích dẫn nguồn ở cuối câu theo định dạng [Document X].
3. Nếu Context không chứa đủ thông tin để trả lời, hãy từ chối: "Tôi không thể xác minh thông tin này từ nguồn hiện có."."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (Lost in the middle mitigation)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có Document index, title và source label để tạo citation."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Tài liệu")
        source = metadata.get("source", "Không rõ nguồn")
        content = chunk.get("content", "").strip()
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{content}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình trong .env."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()

    if provider == "gemini":
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY chưa được cấu hình.")
        genai.configure(api_key=api_key)

        model_name = os.getenv("LLM_MODEL") or LLM_MODEL or "gemini-1.5-flash"
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config={"temperature": TEMPERATURE, "top_p": TOP_P},
        )
        response = model.generate_content(user_message)
        return response.text or ""

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY chưa được cấu hình.")
        client = anthropic.Anthropic(api_key=api_key)

        model_name = os.getenv("LLM_MODEL") or LLM_MODEL or "claude-3-5-haiku-20241022"
        response = client.messages.create(
            model=model_name,
            max_tokens=1024,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text or ""

    else:
        # Mặc định sử dụng OpenAI
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình.")
        client = OpenAI(api_key=api_key)

        model_name = os.getenv("LLM_MODEL") or LLM_MODEL or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model_name,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult chuẩn MODULE_CONTRACTS."""
    if not query or not query.strip():
        return {
            "answer": "Vui lòng nhập câu hỏi để tìm kiếm thông tin.",
            "sources": [],
            "retrieval_source": "none",
        }

    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    # Xác định retrieval_source theo enum: "hybrid" | "pageindex" | "none"
    first_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = "pageindex" if first_method == "pageindex" else "hybrid"

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
        if not answer or not answer.strip():
            answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    except Exception as e:
        print(f"LLM generation failed: {e}")
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có do lỗi kết nối mô hình."

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("Điều kiện hưởng chế độ thai sản là gì?"))

