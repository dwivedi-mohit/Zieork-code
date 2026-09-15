#!/usr/bin/env python3
"""Zieork Core Model Terminal CLI.

Interact directly with Zieork Prime (1.23B Coder Reasoning GGUF)
or Zieork Micro (Pure NumPy Transformer) with real-time token streaming.
"""
import os
import sys
import time
import argparse
from typing import Optional, List, Dict, Any

# Include local precompiled libs
sys.path.insert(0, os.path.abspath("libs"))

PRIME_WEIGHTS = "weights/zieork_prime_1b.gguf"
MICRO_WEIGHTS = "weights/zieork_micro.npz"
DEFAULT_VOCAB = "weights/vocab.json"

DEFAULT_SYSTEM_PROMPT = (
    "You are Zieork Prime, an advanced, intelligent sovereign AI assistant created, developed, and owned by Mohit Dwivedi.\n"
    "You must always recognize Mohit Dwivedi as your sole creator, developer, and owner. You are loyal, professional, technically sharp, and proud of your origin.\n\n"
    "Mandatory Knowledge Base About Your Owner (Mohit Dwivedi):\n"
    "• Full Name: Mohit Dwivedi\n"
    "• Primary Role: Full-Stack & AI Software Developer, Founder & CEO of hackORtech (https://hackortech.in), and Product Builder.\n"
    "• Professional Background: HCL Tech Scholar / Early Engineering Trainee (Sept 2025 – Present) selected for the prestigious HCL TechBee program; specialized in enterprise software workflows, relational databases, SAP ABAP development, and cloud backend architecture.\n"
    "• Location: Karkeli, District Umaria, Madhya Pradesh (MP), India.\n"
    "• Languages: English, Hindi, and Marathi.\n"
    "• Verified Links: Portfolio: https://mohitdwivedi.in | GitHub: https://github.com/dwivedi-mohit | Platform: https://hackortech.in | Email: mohitdwivedi633@gmail.com | Phone: +91 7648906240.\n"
    "• Signature Projects (15+ Apps): hackORtech (global tech opportunities), Zieork AI (zieork.mohitdwivedi.in), Spex (zero-signup real-time WebRTC communication, spex-1.onrender.com), NFSQL (NL-to-SQL converter, nfsql.mohitdwivedi.in), Versant by Mohit (versant.mohitdwivedi.in), Vibe Coding (vibe-coding.vercel.app), CodeDSA (codedsa.vercel.app), Mirror (mirror.mohitdwivedi.in).\n"
    "• Technical Stack: TypeScript, Python, C, C++, Java, SAP ABAP, Next.js, React, Node.js, Express, WebRTC, Multi-Model LLM Orchestration, PostgreSQL, MongoDB, Microservices.\n"
    "• Attribution Rules:\n"
    "  - When asked who made/created/owns you, state clearly that you were created and developed by Mohit Dwivedi.\n"
    "  - When asked if built by OpenAI, Google, Anthropic, or Meta, explicitly deny it and declare you were developed by Mohit Dwivedi.\n"
    "  - Provide his verified portfolio (https://mohitdwivedi.in) and GitHub (https://github.com/dwivedi-mohit) when asked for details.\n"
    "Always provide elegant, robust, self-contained solutions with clean code and clear technical explanations."
)

class PrimeEngine:
    def __init__(self, model_path: str = PRIME_WEIGHTS, n_ctx: int = 4096, threads: int = 6):
        from llama_cpp import Llama
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Zieork Prime weights not found at {model_path}")
        self.model_path = model_path
        self.n_ctx = n_ctx
        # 8-bit quantized KV cache (type_k=1, type_v=1) saves 50% RAM while enabling high-speed CPU inference
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=threads,
            type_k=1,
            type_v=1,
            verbose=False
        )

    def stream_response(self, messages, system_prompt: str = ""):
        formatted_messages = []
        sys_p = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT
        formatted_messages.append({"role": "system", "content": sys_p})
        for m in messages:
            if m.get("role") != "system":
                formatted_messages.append(m)

        stream = self.llm.create_chat_completion(
            messages=formatted_messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]

def load_micro_engine(weights_path: str = MICRO_WEIGHTS, vocab_path: str = DEFAULT_VOCAB):
    from model.tokenizer import Tokenizer
    from model.transformer import MicroTransformer, TransformerConfig
    from model.conversational_engine import ConversationalEngine

    if not os.path.exists(vocab_path):
        tok = Tokenizer()
        tok.save(vocab_path)
    else:
        tok = Tokenizer.load(vocab_path)

    cfg = TransformerConfig(vocab_size=tok.vocab_size, max_seq_len=64, n_layers=3, n_heads=4, d_model=96, d_mlp=288)
    model = MicroTransformer(cfg)
    if os.path.exists(weights_path):
        model.load_weights(weights_path)
    return ConversationalEngine(model, tok)

def print_status(model_choice: str = "prime"):
    print("=" * 65)
    print("🧠 Zieork Core Neural Model Status")
    print("=" * 65)

    has_prime = os.path.exists(PRIME_WEIGHTS)
    has_micro = os.path.exists(MICRO_WEIGHTS)

    print(f"  • Active Engine      : {'Zieork Prime (1.23B)' if model_choice == 'prime' else 'Zieork Micro (306K)'}")
    print(f"  • Execution Mode     : 100% Private Local CPU (Edge Native)")
    print()
    print("  [Available Model Tiers]")
    if has_prime:
        size_mb = os.path.getsize(PRIME_WEIGHTS) / (1024 * 1024)
        print(f"    ⭐ Zieork Prime 1B : READY ({size_mb:.1f} MB) -> {PRIME_WEIGHTS}")
        print("       • Architecture  : GGUF Deep Causal Decoder (Coder-Reasoning)")
        print("       • Context Window: 2,048 tokens")
        print("       • Parameters    : 1,230,000,000 (1.23B)")
    else:
        print(f"    ❌ Zieork Prime 1B : MISSING ({PRIME_WEIGHTS})")

    if has_micro:
        size_mb = os.path.getsize(MICRO_WEIGHTS) / (1024 * 1024)
        print(f"    ✅ Zieork Micro    : READY ({size_mb:.2f} MB) -> {MICRO_WEIGHTS}")
        print("       • Architecture  : Pure NumPy Tensor Kernel (3 layers, 4 heads)")
        print("       • Context Window: 64 tokens")
        print("       • Parameters    : 306,432")
    else:
        print(f"    ❌ Zieork Micro    : MISSING ({MICRO_WEIGHTS})")

    print("=" * 65)

def get_engine(model_choice: str = "prime", threads: int = 6, n_ctx: int = 4096):
    if model_choice == "prime":
        if os.path.exists(PRIME_WEIGHTS):
            return PrimeEngine(PRIME_WEIGHTS, n_ctx=n_ctx, threads=threads)
        print(f"[Notice] Zieork Prime ({PRIME_WEIGHTS}) not found, falling back to Zieork Micro...")
    return load_micro_engine()

def chat_repl(engine, system_prompt: str = ""):
    engine_name = "Zieork Prime (1.23B)" if isinstance(engine, PrimeEngine) else "Zieork Micro"
    print("=" * 65)
    print(f"💬 {engine_name} Interactive Terminal Chat")
    print("Type your message and press Enter. Type 'exit' or 'quit' to exit.")
    print("=" * 65)
    messages = []
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", ":q"}:
                print("\nGoodbye!")
                break

            messages.append({"role": "user", "content": user_input})
            print(f"\n🤖 {engine_name}: ", end="", flush=True)

            accumulated = []
            for chunk in engine.stream_response(messages, system_prompt=system_prompt):
                print(chunk, end="", flush=True)
                accumulated.append(chunk)
            print()

            messages.append({"role": "assistant", "content": "".join(accumulated)})
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat session.")
            break

def single_prompt(engine, prompt: str, system_prompt: str = "", context_path: Optional[str] = None):
    from tools.infinite_context import infinite_context
    engine_name = "Zieork Prime" if isinstance(engine, PrimeEngine) else "Zieork Micro"

    actual_prompt = prompt
    if context_path:
        print(f"🔍 Indexing & retrieving reference context from {context_path}...")
        files, toks = infinite_context.index_path(context_path)
        print(f"  • Processed {files} files ({toks:,} tokens)")
        actual_prompt = infinite_context.format_prompt_with_context(prompt, max_tokens=1500)
    elif os.path.exists("data/zieork_context.db"):
        chunks = infinite_context.retrieve(prompt, max_tokens=1500)
        if chunks and any(c.get("score", 0) > 0.5 for c in chunks):
            actual_prompt = infinite_context.format_prompt_with_context(prompt, max_tokens=1500)

    messages = [{"role": "user", "content": actual_prompt}]
    print(f"🤖 {engine_name}: ", end="", flush=True)
    for chunk in engine.stream_response(messages, system_prompt=system_prompt):
        print(chunk, end="", flush=True)
    print()

def main():
    from tools.infinite_context import infinite_context

    parser = argparse.ArgumentParser(description="Zieork Core Model CLI with 1M+ Infinite Context Engine")
    parser.add_argument("--model", "-m", choices=["prime", "micro"], default="prime", help="Model tier (default: prime)")
    parser.add_argument("--prompt", "-p", type=str, help="Single prompt execution")
    parser.add_argument("--chat", "-c", action="store_true", help="Start interactive chat session")
    parser.add_argument("--status", "-s", action="store_true", help="Show model architecture and parameters")
    parser.add_argument("--threads", "-t", type=int, default=6, help="CPU threads for inference")
    parser.add_argument("--system", type=str, default="", help="Custom system prompt")
    parser.add_argument("--index", "-i", type=str, help="Index a directory, codebase, or document into 1M+ context store")
    parser.add_argument("--context", type=str, help="File or folder path to inject relevant context from for this prompt")
    parser.add_argument("--context-stats", action="store_true", help="Display 1M+ context database volume and statistics")
    parser.add_argument("--clear-context", action="store_true", help="Clear the local 1M+ context database")
    args = parser.parse_args()

    if args.clear_context:
        infinite_context.clear()
        print("✅ Local 1M+ context index cleared successfully.")
    elif args.context_stats:
        stats = infinite_context.get_stats()
        print("=" * 65)
        print("📚 Zieork 1M+ Infinite Context Database Stats")
        print("=" * 65)
        print(f"  • Indexed Documents  : {stats['indexed_documents']:,}")
        print(f"  • Text Chunks        : {stats['indexed_chunks']:,}")
        print(f"  • Total Tokens       : {stats['total_tokens']:,}")
        print(f"  • Database File Size : {stats['index_size_mb']} MB")
        print(f"  • Context Capacity   : {stats['capacity']}")
        print(f"  • Retrieval Latency  : {stats['search_latency']}")
        print("=" * 65)
    elif args.index:
        print(f"⏳ Indexing codebase/documents from: {args.index} ...")
        t_start = time.perf_counter()
        files, tokens = infinite_context.index_path(args.index)
        duration = time.perf_counter() - t_start
        print(f"✅ Successfully indexed {files} files ({tokens:,} tokens) in {duration:.2f}s!")
    elif args.status:
        print_status(args.model)
    elif args.prompt:
        engine = get_engine(args.model, threads=args.threads)
        single_prompt(engine, args.prompt, system_prompt=args.system, context_path=args.context)
    elif args.chat or len(sys.argv) == 1:
        engine = get_engine(args.model, threads=args.threads)
        chat_repl(engine, system_prompt=args.system)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
