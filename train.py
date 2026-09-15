"""Training script for MicroTransformer on instruction dataset."""
import os
import json
import time
import argparse
import numpy as np
from model.tokenizer import Tokenizer
from model.transformer import MicroTransformer, TransformerConfig
from model.optimizer import AdamW

def load_data(data_path: str, tokenizer: Tokenizer, seq_len: int):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_tokens = []
    system_prompt = "You are a helpful and intelligent local AI assistant."

    for item in data:
        inst = item["instruction"]
        resp = item["response"]
        text = f"<|system|>\n{system_prompt}\n<|user|>\n{inst}\n<|assistant|>\n{resp}<EOS>\n"
        tokens = tokenizer.encode(text)
        all_tokens.extend(tokens)

    print(f"Total training tokens: {len(all_tokens)}")
    
    # Create chunks of length seq_len + 1 (for input and target)
    examples_x = []
    examples_y = []
    step = seq_len // 2  # overlapping stride for better data density
    for i in range(0, len(all_tokens) - seq_len, step):
        chunk = all_tokens[i:i + seq_len + 1]
        if len(chunk) == seq_len + 1:
            examples_x.append(chunk[:-1])
            examples_y.append(chunk[1:])

    x_arr = np.array(examples_x, dtype=np.int32)
    y_arr = np.array(examples_y, dtype=np.int32)
    return x_arr, y_arr

def train(
    data_path: str = "data/instructions.json",
    weights_path: str = "weights/zieork_micro.npz",
    vocab_path: str = "weights/vocab.json",
    epochs: int = 50,
    batch_size: int = 4,
    lr: float = 0.003,
    min_lr: float = 0.0003,
    seq_len: int = 64,
    n_layers: int = 3,
    d_model: int = 96,
    n_heads: int = 4,
    d_mlp: int = 288,
):
    print("=" * 60)
    print("🚀 Training Zieork Micro-Transformer from Scratch on CPU")
    print("=" * 60)

    # 1. Initialize Tokenizer & Data
    if os.path.exists(vocab_path):
        tokenizer = Tokenizer.load(vocab_path)
    else:
        tokenizer = Tokenizer()
        tokenizer.save(vocab_path)
    
    x_data, y_data = load_data(data_path, tokenizer, seq_len)
    total_samples = len(x_data)
    print(f"Dataset generated {total_samples} sequence windows of length {seq_len}.")
    print(f"Vocabulary: {vocab_path} (Vocab size: {tokenizer.vocab_size})")

    # 85% train, 15% validation split
    split_idx = int(0.85 * total_samples)
    perm = np.random.permutation(total_samples)
    train_x, train_y = x_data[perm[:split_idx]], y_data[perm[:split_idx]]
    val_x, val_y = x_data[perm[split_idx:]], y_data[perm[split_idx:]]
    num_train = len(train_x)
    num_val = len(val_x)
    print(f"Split: {num_train} train sequences, {num_val} validation sequences.")

    # 2. Configure Model
    cfg = TransformerConfig(
        vocab_size=tokenizer.vocab_size,
        max_seq_len=seq_len,
        n_layers=n_layers,
        n_heads=n_heads,
        d_model=d_model,
        d_mlp=d_mlp,
    )
    model = MicroTransformer(cfg)
    total_params = model.total_parameters
    print(f"Model architecture: {n_layers} layers, {n_heads} heads, {d_model} hidden dim, {d_mlp} mlp dim")
    print(f"Total parameters: {total_params:,} ({model.model_size_mb:.2f} MB in FP32)")
    print("=" * 60)

    optimizer = AdamW(model.params, lr=lr, weight_decay=0.01)

    start_time = time.time()
    steps_per_epoch = max(1, num_train // batch_size)

    for epoch in range(1, epochs + 1):
        # Cosine Annealing learning rate
        current_lr = min_lr + 0.5 * (lr - min_lr) * (1.0 + np.cos(np.pi * (epoch - 1) / max(1, epochs)))
        
        indices = np.random.permutation(num_train)
        epoch_loss = 0.0

        for step in range(steps_per_epoch):
            batch_idx = indices[step * batch_size : (step + 1) * batch_size]
            batch_x = train_x[batch_idx]
            batch_y = train_y[batch_idx]

            # Forward pass
            logits, cache = model.forward(batch_x)
            loss, dlogits = model.compute_loss(logits, batch_y)
            epoch_loss += loss

            # Backward pass & AdamW step
            grads = model.backward(dlogits, cache)
            optimizer.step(grads, custom_lr=current_lr)

        avg_train_loss = epoch_loss / steps_per_epoch

        # Evaluate validation loss
        val_loss = 0.0
        if num_val > 0:
            val_logits, _ = model.forward(val_x)
            val_loss, _ = model.compute_loss(val_logits, val_y)

        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            elapsed = time.time() - start_time
            val_str = f" | Val Loss: {val_loss:.4f}" if num_val > 0 else ""
            print(f"Epoch [{epoch:03d}/{epochs:03d}] | LR: {current_lr:.6f} | Train Loss: {avg_train_loss:.4f}{val_str} | Perplexity: {np.exp(min(avg_train_loss, 20)):.2f} | Time: {elapsed:.1f}s")

    # Save trained weights
    model.save_weights(weights_path)
    file_size_mb = os.path.getsize(weights_path) / (1024 * 1024)
    print("=" * 60)
    print(f"✅ Training completed in {time.time() - start_time:.1f} seconds!")
    print(f"💾 Model weights saved to: {weights_path}")
    print(f"📦 Final disk size: {file_size_mb:.2f} MB (Target: < 100 MB)")
    print("=" * 60)

    # Test generation
    test_prompt = "<|user|>\nWhat is AI?\n<|assistant|>\n"
    tokens = tokenizer.encode(test_prompt)
    output_tokens = model.generate(tokens, max_new_tokens=60, temperature=0.7, eos_token_id=tokenizer.eos_id)
    generated_text = tokenizer.decode(output_tokens)
    print("Sample generation test:")
    print("-" * 40)
    print(generated_text)
    print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MicroTransformer")
    parser.add_argument("--epochs", type=int, default=30, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.003, help="Learning rate")
    parser.add_argument("--seq_len", type=int, default=64, help="Sequence length")
    parser.add_argument("--weights", type=str, default="weights/zieork_micro.npz", help="Weights save path")
    args = parser.parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        seq_len=args.seq_len,
        weights_path=args.weights,
    )
