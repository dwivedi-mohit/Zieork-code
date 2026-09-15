#!/usr/bin/env python3
"""Zieork Weights Manager & Downloader.

Allows downloading, verifying, and setting up sovereign neural weights
for Zieork Micro (NumPy CPU), Zieork Fast (135M GGUF), and Zieork Prime (1B GGUF).
"""
import os
import sys
import argparse
import urllib.request

WEIGHTS_DIR = os.path.abspath("weights")

MODELS = {
    "zieork-micro": {
        "filename": "zieork_micro.npz",
        "description": "NumPy Causal Decoder-Only Transformer (306K params, CPU edge native)",
        "included_in_repo": True,
    },
    "zieork-fast": {
        "filename": "zieork_fast_135m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "description": "Fast quantized GGUF edge model for real-time tool calling",
        "included_in_repo": False,
    },
    "zieork-prime": {
        "filename": "zieork_prime_1b.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "description": "Prime sovereign coding reasoning model (1B+ params GGUF)",
        "included_in_repo": False,
    }
}

def verify_weights():
    print("=" * 60)
    print("🔍 Zieork Neural Weights Status")
    print("=" * 60)
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    all_ready = True
    for key, info in MODELS.items():
        path = os.path.join(WEIGHTS_DIR, info["filename"])
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  ✅ {key.ljust(15)}: FOUND ({size_mb:.2f} MB) -> {path}")
        else:
            print(f"  ❌ {key.ljust(15)}: MISSING -> {path}")
            if not info.get("included_in_repo", False):
                all_ready = False

    vocab_path = os.path.join(WEIGHTS_DIR, "vocab.json")
    if os.path.exists(vocab_path):
        print(f"  ✅ {'vocab.json'.ljust(15)}: FOUND -> {vocab_path}")
    else:
        print(f"  ❌ {'vocab.json'.ljust(15)}: MISSING -> {vocab_path}")

    print("=" * 60)
    return all_ready

def download_model(model_key: str):
    if model_key not in MODELS:
        print(f"Unknown model: {model_key}. Available: {list(MODELS.keys())}")
        return False

    info = MODELS[model_key]
    dest = os.path.join(WEIGHTS_DIR, info["filename"])
    if os.path.exists(dest):
        print(f"Model {model_key} already exists at {dest}.")
        return True

    url = info.get("url")
    if not url:
        print(f"Model {model_key} is trained locally with `python3 train.py`.")
        return False

    print(f"Downloading {model_key} from {url}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Successfully downloaded to {dest}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zieork Weights Manager")
    parser.add_argument("--status", action="store_true", help="Check status of all weights")
    parser.add_argument("--download", type=str, choices=list(MODELS.keys()) + ["all"], help="Download model")
    args = parser.parse_args()

    if args.download:
        if args.download == "all":
            for m in MODELS:
                download_model(m)
        else:
            download_model(args.download)
    else:
        verify_weights()
