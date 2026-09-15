#!/usr/bin/env python3
"""Zieork Core Model Terminal CLI.

Interact directly with Zieork Prime (1.23B Coder Reasoning GGUF)
or Zieork Micro (Pure NumPy Transformer) with real-time token streaming.
"""
import os
import sys
import time
import argparse

# Include local precompiled libs
sys.path.insert(0, os.path.abspath("libs"))

PRIME_WEIGHTS = "weights/zieork_prime_1b.gguf"
MICRO_WEIGHTS = "weights/zieork_micro.npz"
DEFAULT_VOCAB = "weights/vocab.json"

DEFAULT_SYSTEM_PROMPT = (
    "You are Zieork Prime, an advanced sovereign reasoning and code synthesis neural operating system. "
    "You execute directly on private local edge hardware with zero cloud dependency. "
    "Provide elegant, robust, self-contained solutions with clear technical explanations."
)

class PrimeEngine:
    def __init__(self, model_path: str = PRIME_WEIGHTS, n_ctx: int = 2048, threads: int = 6):
        from llama_cpp import Llama
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Zieork Prime weights not found at {model_path}")
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=threads, verbose=False)

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

def get_engine(model_choice: str = "prime", threads: int = 6):
    if model_choice == "prime":
        if os.path.exists(PRIME_WEIGHTS):
            return PrimeEngine(PRIME_WEIGHTS, n_ctx=2048, threads=threads)
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

def single_prompt(engine, prompt: str, system_prompt: str = ""):
    engine_name = "Zieork Prime" if isinstance(engine, PrimeEngine) else "Zieork Micro"
    messages = [{"role": "user", "content": prompt}]
    print(f"🤖 {engine_name}: ", end="", flush=True)
    for chunk in engine.stream_response(messages, system_prompt=system_prompt):
        print(chunk, end="", flush=True)
    print()

def main():
    parser = argparse.ArgumentParser(description="Zieork Core Model CLI")
    parser.add_argument("--model", "-m", choices=["prime", "micro"], default="prime", help="Model tier (default: prime)")
    parser.add_argument("--prompt", "-p", type=str, help="Single prompt execution")
    parser.add_argument("--chat", "-c", action="store_true", help="Start interactive chat session")
    parser.add_argument("--status", "-s", action="store_true", help="Show model architecture and parameters")
    parser.add_argument("--threads", "-t", type=int, default=6, help="CPU threads for inference")
    parser.add_argument("--system", type=str, default="", help="Custom system prompt")
    args = parser.parse_args()

    if args.status:
        print_status(args.model)
    elif args.prompt:
        engine = get_engine(args.model, threads=args.threads)
        single_prompt(engine, args.prompt, system_prompt=args.system)
    elif args.chat or len(sys.argv) == 1:
        engine = get_engine(args.model, threads=args.threads)
        chat_repl(engine, system_prompt=args.system)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
