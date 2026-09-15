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

from tools.sampling_config import (
    CHATGPT_BEHAVIORAL_SYSTEM_PROMPT,
    PRESETS,
    get_preset,
    SamplingPreset
)

DEFAULT_SYSTEM_PROMPT = CHATGPT_BEHAVIORAL_SYSTEM_PROMPT

class PrimeEngine:
    def __init__(self, model_path: str = PRIME_WEIGHTS, n_ctx: int = 4096, threads: int = 8, preset_name: str = "chatgpt"):
        from llama_cpp import Llama
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Zieork Prime weights not found at {model_path}")
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.preset = get_preset(preset_name)
        # 8-bit quantized KV cache (type_k=1, type_v=1) saves 50% RAM while enabling high-speed CPU inference
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=threads,
            type_k=1,
            type_v=1,
            verbose=False
        )

    def set_preset(self, preset_name: str) -> SamplingPreset:
        """Dynamically switch sampling preset."""
        self.preset = get_preset(preset_name)
        return self.preset

    def stream_response(self, messages, system_prompt: str = "", preset_override: Optional[SamplingPreset] = None):
        formatted_messages = []
        sys_p = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT
        formatted_messages.append({"role": "system", "content": sys_p})
        for m in messages:
            if m.get("role") != "system":
                formatted_messages.append(m)

        active_preset = preset_override or self.preset
        stream = self.llm.create_chat_completion(
            messages=formatted_messages,
            max_tokens=1024,
            stream=True,
            **active_preset.to_dict()
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

def get_engine(model_choice: str = "prime", threads: int = 8, n_ctx: int = 4096, preset_name: str = "chatgpt"):
    if model_choice == "prime":
        if os.path.exists(PRIME_WEIGHTS):
            return PrimeEngine(PRIME_WEIGHTS, n_ctx=n_ctx, threads=threads, preset_name=preset_name)
        print(f"[Notice] Zieork Prime ({PRIME_WEIGHTS}) not found, falling back to Zieork Micro...")
    return load_micro_engine()

def compact_conversation_messages(messages: List[Dict[str, str]], max_token_budget: int = 3000) -> List[Dict[str, str]]:
    """Prune or compact earlier conversation turns to prevent context boundary overflow."""
    if not messages:
        return []
    total_words = sum(len(m.get("content", "").split()) for m in messages)
    approx_tokens = total_words * 4 // 3
    if approx_tokens <= max_token_budget:
        return messages

    # Keep the most recent 6 messages to preserve immediate continuity
    if len(messages) > 6:
        return messages[-6:]
    return messages

def chat_repl(engine, system_prompt: str = ""):
    is_prime = isinstance(engine, PrimeEngine)
    engine_name = "Zieork Prime (1.23B)" if is_prime else "Zieork Micro"
    preset_name = engine.preset.name if is_prime else "micro-standard"

    print("=" * 68)
    print(f"💬 \033[1;36m{engine_name}\033[0m \033[1mInteractive ChatGPT-Style Session\033[0m")
    print("  • Sovereign Edge Execution | Created & Owned by Mohit Dwivedi")
    print(f"  • Active Preset: \033[1;32m{preset_name}\033[0m | Context Budget: 4,096 tokens")
    print("  • In-chat commands: \033[93m/help, /clear, /preset <name>, /history, /save, exit\033[0m")
    print("=" * 68)

    messages = []
    active_sys_prompt = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT

    while True:
        try:
            user_input = input("\n\033[1;32m👤 You\033[0m: ").strip()
            if not user_input:
                continue

            # Command: exit / quit
            if user_input.lower() in {"exit", "quit", ":q"}:
                print("\n\033[90mExiting session. Have a productive day!\033[0m")
                break

            # Command: /help
            if user_input.lower() == "/help":
                print("\n\033[1m📚 Available In-Chat Slash Commands:\033[0m")
                print("  • \033[93m/clear\033[0m or \033[93m/reset\033[0m    : Reset conversation history")
                print("  • \033[93m/history\033[0m              : View turn count and estimated tokens")
                print("  • \033[93m/preset <name>\033[0m        : Switch preset (chatgpt, code, creative, precise)")
                print("  • \033[93m/system <prompt>\033[0m      : View or update active behavioral persona")
                print("  • \033[93m/save [filename]\033[0m      : Export conversation transcript")
                print("  • \033[93m/stats\033[0m                : Display engine specs and RAM state")
                continue

            # Command: /clear or /reset
            if user_input.lower() in {"/clear", "/reset"}:
                messages.clear()
                print("\033[92m✨ Conversation history cleared successfully.\033[0m")
                continue

            # Command: /history
            if user_input.lower() == "/history":
                tok_est = sum(len(m.get("content", "").split()) for m in messages) * 4 // 3
                print(f"\n\033[1m📜 Conversation History:\033[0m {len(messages)} turns (~{tok_est:,} tokens)")
                for idx, m in enumerate(messages, 1):
                    role = m["role"].upper()
                    snippet = m["content"][:60].replace("\n", " ") + "..."
                    print(f"   {idx}. [{role}] {snippet}")
                continue

            # Command: /preset <name>
            if user_input.lower().startswith("/preset"):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1 and is_prime:
                    new_preset = parts[1].strip()
                    p = engine.set_preset(new_preset)
                    print(f"\033[92m⚙️ Switched preset to '{p.name}' (temp={p.temperature}, top_p={p.top_p}, rep_pen={p.repeat_penalty})\033[0m")
                elif is_prime:
                    print(f"\033[1mAvailable presets:\033[0m {', '.join(PRESETS.keys())} (current: {engine.preset.name})")
                else:
                    print("\033[93mPresets are available on Zieork Prime (1.23B).\033[0m")
                continue

            # Command: /system
            if user_input.lower().startswith("/system"):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    active_sys_prompt = parts[1].strip()
                    print("\033[92m⚙️ System prompt updated for current session.\033[0m")
                else:
                    print(f"\n\033[1mActive System Persona:\033[0m\n{active_sys_prompt}\n")
                continue

            # Command: /save
            if user_input.lower().startswith("/save"):
                parts = user_input.split(maxsplit=1)
                filename = parts[1].strip() if len(parts) > 1 else f"session_{int(time.time())}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# Zieork Chat Session Export - {time.ctime()}\n\n")
                    for m in messages:
                        f.write(f"### {m['role'].upper()}:\n{m['content']}\n\n")
                print(f"\033[92m💾 Session transcript saved to: {filename}\033[0m")
                continue

            # Command: /stats
            if user_input.lower() == "/stats":
                print(f"\n\033[1m⚙️ Zieork Session Metrics:\033[0m")
                print(f"  • Model Engine : {engine_name}")
                if is_prime:
                    print(f"  • Preset       : {engine.preset.name} (T={engine.preset.temperature}, P={engine.preset.top_p})")
                    print(f"  • Repeat Pen   : {engine.preset.repeat_penalty}")
                    print(f"  • Context Size : {engine.n_ctx} tokens")
                print(f"  • Cached Turns : {len(messages)}")
                continue

            # User message submission
            messages.append({"role": "user", "content": user_input})
            messages = compact_conversation_messages(messages)

            print(f"\n\033[1;36m🤖 {engine_name}\033[0m:\n", flush=True)

            t_start = time.perf_counter()
            accumulated = []
            tok_count = 0

            for chunk in engine.stream_response(messages, system_prompt=active_sys_prompt):
                print(chunk, end="", flush=True)
                accumulated.append(chunk)
                tok_count += 1

            duration = max(time.perf_counter() - t_start, 0.001)
            tok_rate = tok_count / duration
            print(f"\n\n\033[90m[⏱️ {duration:.2f}s | {tok_count} tokens | {tok_rate:.1f} tok/s | preset: {engine.preset.name if is_prime else 'micro'}]\033[0m")

            messages.append({"role": "assistant", "content": "".join(accumulated)})

        except (KeyboardInterrupt, EOFError):
            print("\n\033[90mExiting chat session.\033[0m")
            break

def single_prompt(engine, prompt: str, system_prompt: str = "", context_path: Optional[str] = None):
    from tools.infinite_context import infinite_context
    is_prime = isinstance(engine, PrimeEngine)
    engine_name = "Zieork Prime" if is_prime else "Zieork Micro"

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
    print(f"\033[1;36m🤖 {engine_name}\033[0m:\n", flush=True)
    t_start = time.perf_counter()
    tok_count = 0

    for chunk in engine.stream_response(messages, system_prompt=system_prompt):
        print(chunk, end="", flush=True)
        tok_count += 1

    duration = max(time.perf_counter() - t_start, 0.001)
    tok_rate = tok_count / duration
    print(f"\n\n\033[90m[⏱️ {duration:.2f}s | {tok_count} tokens | {tok_rate:.1f} tok/s]\033[0m")

def main():
    from tools.infinite_context import infinite_context

    parser = argparse.ArgumentParser(description="Zieork Core Model CLI with 1M+ Infinite Context Engine & ChatGPT Presets")
    parser.add_argument("--model", "-m", choices=["prime", "micro"], default="prime", help="Model tier (default: prime)")
    parser.add_argument("--prompt", "-p", type=str, help="Single prompt execution")
    parser.add_argument("--chat", "-c", action="store_true", help="Start interactive chat session")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), default="chatgpt", help="Decoding preset (chatgpt, code, creative, precise)")
    parser.add_argument("--status", "-s", action="store_true", help="Show model architecture and parameters")
    parser.add_argument("--threads", "-t", type=int, default=8, help="CPU threads for inference (default: 8)")
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
        engine = get_engine(args.model, threads=args.threads, preset_name=args.preset)
        single_prompt(engine, args.prompt, system_prompt=args.system, context_path=args.context)
    elif args.chat or len(sys.argv) == 1:
        engine = get_engine(args.model, threads=args.threads, preset_name=args.preset)
        chat_repl(engine, system_prompt=args.system)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
