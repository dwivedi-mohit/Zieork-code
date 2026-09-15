#!/usr/bin/env python3
"""Zieork Core Model Terminal CLI.

Interact directly with the sovereign MicroTransformer neural model
for real-time CPU generation, streaming responses, and model diagnostics.
"""
import os
import sys
import time
import argparse
from model.tokenizer import Tokenizer
from model.transformer import MicroTransformer, TransformerConfig
from model.conversational_engine import ConversationalEngine

DEFAULT_WEIGHTS = "weights/zieork_micro.npz"
DEFAULT_VOCAB = "weights/vocab.json"

def load_engine(weights_path: str = DEFAULT_WEIGHTS, vocab_path: str = DEFAULT_VOCAB) -> ConversationalEngine:
    if not os.path.exists(vocab_path):
        tok = Tokenizer()
        tok.save(vocab_path)
    else:
        tok = Tokenizer.load(vocab_path)

    cfg = TransformerConfig(vocab_size=tok.vocab_size, max_seq_len=64, n_layers=3, n_heads=4, d_model=96, d_mlp=288)
    model = MicroTransformer(cfg)

    if os.path.exists(weights_path):
        model.load_weights(weights_path)
    else:
        print(f"[Warning] Weights not found at {weights_path}, using random initialization.")

    return ConversationalEngine(model, tok)

def print_status(weights_path: str = DEFAULT_WEIGHTS, vocab_path: str = DEFAULT_VOCAB):
    print("=" * 60)
    print("🧠 Zieork Core Neural Model Status")
    print("=" * 60)
    engine = load_engine(weights_path, vocab_path)
    m = engine.model
    tok = engine.tokenizer
    print(f"  • Architecture      : {m.config.n_layers} Layers, {m.config.n_heads} Heads, {m.config.d_model} Hidden Dim")
    print(f"  • MLP Inner Dim     : {m.config.d_mlp}")
    print(f"  • Context Window    : {m.config.max_seq_len} tokens")
    print(f"  • Vocabulary Size   : {tok.vocab_size} tokens ({'Character/Byte ASCII' if tok.is_char_vocab else 'Subword'})")
    print(f"  • Total Parameters  : {m.total_parameters:,} ({m.model_size_mb:.2f} MB in FP32)")
    print(f"  • Execution Device  : 100% Private Local CPU (NumPy Kernel)")
    print(f"  • Weights File      : {weights_path} ({'FOUND' if os.path.exists(weights_path) else 'MISSING'})")
    print(f"  • Vocab File        : {vocab_path} ({'FOUND' if os.path.exists(vocab_path) else 'MISSING'})")
    print("=" * 60)

def chat_repl(engine: ConversationalEngine, system_prompt: str = ""):
    print("=" * 60)
    print("💬 Zieork Sovereign Model Interactive Terminal Chat")
    print("Type your message and press Enter. Type 'exit' or 'quit' to stop.")
    print("=" * 60)
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
            print("\n🤖 Zieork: ", end="", flush=True)

            accumulated = []
            for chunk in engine.stream_response(messages, system_prompt=system_prompt):
                print(chunk, end="", flush=True)
                accumulated.append(chunk)
            print()

            messages.append({"role": "assistant", "content": "".join(accumulated)})
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat session.")
            break

def single_prompt(engine: ConversationalEngine, prompt: str, system_prompt: str = ""):
    messages = [{"role": "user", "content": prompt}]
    print("🤖 Zieork: ", end="", flush=True)
    for chunk in engine.stream_response(messages, system_prompt=system_prompt):
        print(chunk, end="", flush=True)
    print()

def main():
    parser = argparse.ArgumentParser(description="Zieork Core Model CLI")
    parser.add_argument("--prompt", "-p", type=str, help="Single prompt execution")
    parser.add_argument("--chat", "-c", action="store_true", help="Start interactive chat session")
    parser.add_argument("--status", "-s", action="store_true", help="Show model architecture and parameters")
    parser.add_argument("--weights", type=str, default=DEFAULT_WEIGHTS, help="Weights path")
    parser.add_argument("--vocab", type=str, default=DEFAULT_VOCAB, help="Vocab path")
    parser.add_argument("--system", type=str, default="", help="Custom system prompt")
    args = parser.parse_args()

    if args.status:
        print_status(args.weights, args.vocab)
    elif args.prompt:
        engine = load_engine(args.weights, args.vocab)
        single_prompt(engine, args.prompt, system_prompt=args.system)
    elif args.chat or len(sys.argv) == 1:
        engine = load_engine(args.weights, args.vocab)
        chat_repl(engine, system_prompt=args.system)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
