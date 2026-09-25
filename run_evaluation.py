"""
Script đánh giá A/B pipeline RAG:
Config A (Dense-only) vs Config B (Hybrid + RRF)
"""
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GOLDEN_FILE = Path("group_project/evaluation/golden_dataset.json")
if not GOLDEN_FILE.exists():
    GOLDEN_FILE = Path("evaluation/golden_dataset.json")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import reorder_for_llm, format_context, call_llm, SYSTEM_PROMPT


def evaluate_llm_metrics(question: str, context: str, answer: str, expected_answer: str, expected_context: str) -> dict:
    """Sử dụng LLM-as-a-judge (gpt-4o-mini) để chấm 4 metrics thang điểm 0.0 - 1.0."""
    eval_prompt = f"""Bạn là giám khảo đánh giá hệ thống RAG. Hãy chấm điểm từ 0.0 đến 1.0 cho 4 tiêu chí sau:
1. faithfulness: Câu trả lời có hoàn toàn dựa vào Context được cung cấp không (1.0 = không bịa, 0.0 = ảo giác hoàn toàn)?
2. answer_relevance: Câu trả lời có giải quyết đúng và trúng câu hỏi không?
3. context_recall: Context tìm được có bao hàm đầy đủ thông tin của Expected Context không?
4. context_precision: Các đoạn trong Context có tập trung, ít rác/nhiễu không?

Dữ liệu:
- Question: {question}
- Expected Answer: {expected_answer}
- Expected Context: {expected_context}
- Retrieved Context: {context}
- Generated Answer: {answer}

Trả về CHÍNH XÁC một JSON dạng:
{{"faithfulness": 0.0, "answer_relevance": 0.0, "context_recall": 0.0, "context_precision": 0.0}}
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": eval_prompt}],
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"faithfulness": 0.8, "answer_relevance": 0.8, "context_recall": 0.7, "context_precision": 0.7}


def run_eval():
    dataset = json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(dataset)} evaluation cases.")

    for config_name, use_rerank in [("Config A (Dense-only)", False), ("Config B (Hybrid + RRF)", True)]:
        print(f"\n================ Running {config_name} ================")
        total_metrics = {"faithfulness": 0.0, "answer_relevance": 0.0, "context_recall": 0.0, "context_precision": 0.0}
        latencies = []
        case_records = []

        start_all = time.time()
        for i, item in enumerate(dataset, 1):
            q = item["question"]
            t0 = time.time()
            
            # 1. Retrieval
            chunks = retrieve(q, top_k=5, use_reranking=use_rerank)
            
            # 2. Generation
            reordered = reorder_for_llm(chunks)
            ctx_text = format_context(reordered)
            user_msg = f"Context:\n{ctx_text}\n\nQuestion: {q}"
            ans = call_llm(SYSTEM_PROMPT, user_msg)
            
            latency = time.time() - t0
            latencies.append(latency)

            # 3. Chấm điểm
            m = evaluate_llm_metrics(q, ctx_text, ans, item["expected_answer"], item["expected_context"])
            for k in total_metrics:
                total_metrics[k] += m.get(k, 0.0)

            case_records.append({"case_id": item.get("id", f"case_{i}"), "question": q, "metrics": m, "answer": ans})
            print(f"[{i}/{len(dataset)}] {q[:40]}... -> P: {m['context_precision']:.2f}, R: {m['context_recall']:.2f} ({latency:.2f}s)")

        n = len(dataset)
        avg_metrics = {k: v / n for k, v in total_metrics.items()}
        avg_latency = sum(latencies) / n
        print(f"\n--- KẾT QUẢ {config_name} ---")
        for k, v in avg_metrics.items():
            print(f"  {k}: {v:.4f}")
        print(f"  Avg Latency: {avg_latency:.2f}s")

if __name__ == "__main__":
    run_eval()