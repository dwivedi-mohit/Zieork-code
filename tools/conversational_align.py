"""Open-Source Conversational Alignment and Benchmark Engine for Zieork Prime.

Validates conversational datasets, prepares alignment data, and executes
comparative benchmarks evaluating response structure, tone, and repetition control.
"""
import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any, Tuple

# Include local precompiled libs
sys.path.insert(0, os.path.abspath("libs"))
sys.path.insert(0, os.path.abspath("."))

from tools.sampling_config import PRESETS, get_preset, CHATGPT_BEHAVIORAL_SYSTEM_PROMPT

DATASET_PATH = "data/conversational_alignment_dataset.jsonl"
PRIME_WEIGHTS = "weights/zieork_prime_1b.gguf"

def validate_dataset(filepath: str = DATASET_PATH) -> Dict[str, Any]:
    """Validate JSONL conversational alignment dataset."""
    if not os.path.exists(filepath):
        return {"valid": False, "error": f"File {filepath} does not exist"}

    total_samples = 0
    total_messages = 0
    roles_count = {"system": 0, "user": 0, "assistant": 0}
    total_tokens_est = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                return {"valid": False, "error": f"Invalid JSON on line {idx}: {e}"}

            messages = record.get("messages", [])
            if not messages:
                return {"valid": False, "error": f"Missing 'messages' on line {idx}"}

            total_samples += 1
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role in roles_count:
                    roles_count[role] += 1
                total_tokens_est += len(content.split()) * 4 // 3
                total_messages += 1

    return {
        "valid": True,
        "samples": total_samples,
        "total_messages": total_messages,
        "roles": roles_count,
        "estimated_tokens": total_tokens_est,
        "filepath": filepath
    }

def calculate_repetition_rate(text: str, n: int = 4) -> float:
    """Calculate n-gram repetition rate to detect degenerate looping."""
    words = [w.lower().strip() for w in text.split() if w.strip()]
    if len(words) < n:
        return 0.0
    ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    unique_ngrams = set(ngrams)
    return 1.0 - (len(unique_ngrams) / len(ngrams)) if ngrams else 0.0

def score_markdown_structure(text: str) -> Dict[str, Any]:
    """Score markdown structure (headings, code blocks, lists)."""
    has_headings = "#" in text
    has_code_block = "```" in text
    has_bullet_points = "\n* " in text or "\n- " in text or "\n• " in text or "\n1." in text
    has_bold = "**" in text
    
    score = sum([has_headings, has_code_block, has_bullet_points, has_bold])
    return {
        "score_out_of_4": score,
        "has_headings": has_headings,
        "has_code_block": has_code_block,
        "has_bullet_points": has_bullet_points,
        "has_bold": has_bold
    }

def run_comparative_benchmark(prompt: str, max_tokens: int = 250) -> Dict[str, Any]:
    """Compare baseline generation vs ChatGPT-aligned generation."""
    if not os.path.exists(PRIME_WEIGHTS):
        return {"error": f"Model weights {PRIME_WEIGHTS} not found"}

    from llama_cpp import Llama

    llm = Llama(
        model_path=PRIME_WEIGHTS,
        n_ctx=2048,
        n_threads=8,
        type_k=1,
        type_v=1,
        verbose=False
    )

    # 1. Baseline Run (No Persona, Default Greedy/Unconstrained Sampling)
    baseline_msgs = [{"role": "user", "content": prompt}]
    t0 = time.perf_counter()
    res_base = llm.create_chat_completion(
        messages=baseline_msgs,
        max_tokens=max_tokens,
        temperature=0.7
    )
    t_base = time.perf_counter() - t0
    base_text = res_base["choices"][0]["message"]["content"] or ""

    # 2. ChatGPT-Aligned Run (Behavioral System Prompt + Tuned Presets)
    chatgpt_preset = get_preset("chatgpt")
    aligned_msgs = [
        {"role": "system", "content": CHATGPT_BEHAVIORAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    t1 = time.perf_counter()
    res_aligned = llm.create_chat_completion(
        messages=aligned_msgs,
        max_tokens=max_tokens,
        **chatgpt_preset.to_dict()
    )
    t_aligned = time.perf_counter() - t1
    aligned_text = res_aligned["choices"][0]["message"]["content"] or ""

    # Evaluate metrics
    base_struct = score_markdown_structure(base_text)
    aligned_struct = score_markdown_structure(aligned_text)

    base_rep = calculate_repetition_rate(base_text)
    aligned_rep = calculate_repetition_rate(aligned_text)

    creator_in_base = "mohit" in base_text.lower()
    creator_in_aligned = "mohit" in aligned_text.lower() or "zieork" in aligned_text.lower()

    return {
        "prompt": prompt,
        "baseline": {
            "text": base_text,
            "duration_sec": round(t_base, 2),
            "tokens_est": len(base_text.split()),
            "markdown_score": base_struct["score_out_of_4"],
            "repetition_rate": round(base_rep, 4),
            "creator_acknowledged": creator_in_base
        },
        "chatgpt_aligned": {
            "text": aligned_text,
            "duration_sec": round(t_aligned, 2),
            "tokens_est": len(aligned_text.split()),
            "markdown_score": aligned_struct["score_out_of_4"],
            "repetition_rate": round(aligned_rep, 4),
            "creator_acknowledged": creator_in_aligned
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Zieork Conversational Alignment & Benchmark Tool")
    parser.add_argument("--validate", action="store_true", help="Validate alignment dataset")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative benchmark")
    parser.add_argument("--prompt", type=str, default="Write a python function to check if a number is prime and explain how it works.", help="Benchmark prompt")
    args = parser.parse_args()

    if args.validate or len(sys.argv) == 1:
        res = validate_dataset()
        print("=" * 60)
        print("📊 Conversational Alignment Dataset Validation")
        print("=" * 60)
        print(f"  • Valid Format       : {res.get('valid')}")
        print(f"  • Total Samples      : {res.get('samples')}")
        print(f"  • Total Messages     : {res.get('total_messages')}")
        print(f"  • Roles Distribution : {res.get('roles')}")
        print(f"  • Estimated Tokens   : {res.get('estimated_tokens'):,}")
        print(f"  • File Path          : {res.get('filepath')}")
        print("=" * 60)

    if args.benchmark:
        print("\n⏳ Running Live Comparative Benchmark (Baseline vs. ChatGPT-Aligned)...")
        results = run_comparative_benchmark(args.prompt)
        print("\n" + "=" * 60)
        print("🧪 COMPARATIVE BENCHMARK RESULTS")
        print("=" * 60)
        print(f"Prompt: {results['prompt']}\n")

        print("--- [1] Baseline Output (Raw Unconstrained) ---")
        print(results["baseline"]["text"])
        print(f"\n  • Struct Score : {results['baseline']['markdown_score']}/4")
        print(f"  • Repetition   : {results['baseline']['repetition_rate']:.2%}")
        print(f"  • Latency      : {results['baseline']['duration_sec']}s")

        print("\n--- [2] ChatGPT-Aligned Output (Tuned Physics + Persona) ---")
        print(results["chatgpt_aligned"]["text"])
        print(f"\n  • Struct Score : {results['chatgpt_aligned']['markdown_score']}/4")
        print(f"  • Repetition   : {results['chatgpt_aligned']['repetition_rate']:.2%}")
        print(f"  • Latency      : {results['chatgpt_aligned']['duration_sec']}s")
        print("=" * 60)

if __name__ == "__main__":
    main()
