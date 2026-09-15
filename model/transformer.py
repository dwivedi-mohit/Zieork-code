"""Full Causal Decoder-Only Transformer built from scratch in pure vectorized NumPy."""
import numpy as np
import os
from typing import Dict, List, Optional, Tuple, Generator

class TransformerConfig:
    def __init__(
        self,
        vocab_size: int = 128,
        max_seq_len: int = 128,
        n_layers: int = 4,
        n_heads: int = 4,
        d_model: int = 128,
        d_mlp: int = 384,
    ):
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.d_model = d_model
        self.d_head = d_model // n_heads
        self.d_mlp = d_mlp

    def to_dict(self) -> dict:
        return {
            "vocab_size": self.vocab_size,
            "max_seq_len": self.max_seq_len,
            "n_layers": self.n_layers,
            "n_heads": self.n_heads,
            "d_model": self.d_model,
            "d_mlp": self.d_mlp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TransformerConfig":
        return cls(**d)


def gelu(x: np.ndarray) -> np.ndarray:
    """Gaussian Error Linear Unit (GELU) activation function."""
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * np.power(x, 3))))


def gelu_grad(x: np.ndarray) -> np.ndarray:
    """Analytical gradient of GELU activation function."""
    sqrt_2_pi = np.sqrt(2.0 / np.pi)
    x3 = 0.044715 * np.power(x, 3)
    u = sqrt_2_pi * (x + x3)
    tanh_u = np.tanh(u)
    sech2_u = 1.0 - tanh_u ** 2
    du_dx = sqrt_2_pi * (1.0 + 3.0 * 0.044715 * (x ** 2))
    return 0.5 * (1.0 + tanh_u) + 0.5 * x * sech2_u * du_dx


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    x_max = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - x_max)
    return exp_x / (np.sum(exp_x, axis=axis, keepdims=True) + 1e-12)


class MicroTransformer:
    def __init__(self, config: TransformerConfig):
        self.config = config
        self.params: Dict[str, np.ndarray] = {}
        self._init_weights()

    def _init_weights(self):
        """Initialize all model weights using Xavier/He normal scaling."""
        cfg = self.config
        scale = 0.02

        # 1. Embeddings
        self.params["wte"] = np.random.randn(cfg.vocab_size, cfg.d_model) * scale
        self.params["wpe"] = np.random.randn(cfg.max_seq_len, cfg.d_model) * scale

        # 2. Transformer Layers
        for l in range(cfg.n_layers):
            p = f"layer_{l}."
            # LayerNorm 1
            self.params[p + "ln1_gamma"] = np.ones((cfg.d_model,))
            self.params[p + "ln1_beta"] = np.zeros((cfg.d_model,))

            # Multi-Head Attention (Q, K, V, Out)
            self.params[p + "wq"] = np.random.randn(cfg.d_model, cfg.d_model) * np.sqrt(2.0 / (cfg.d_model + cfg.d_model))
            self.params[p + "wk"] = np.random.randn(cfg.d_model, cfg.d_model) * np.sqrt(2.0 / (cfg.d_model + cfg.d_model))
            self.params[p + "wv"] = np.random.randn(cfg.d_model, cfg.d_model) * np.sqrt(2.0 / (cfg.d_model + cfg.d_model))
            self.params[p + "wo"] = np.random.randn(cfg.d_model, cfg.d_model) * np.sqrt(2.0 / (cfg.d_model + cfg.d_model))

            self.params[p + "bq"] = np.zeros((cfg.d_model,))
            self.params[p + "bk"] = np.zeros((cfg.d_model,))
            self.params[p + "bv"] = np.zeros((cfg.d_model,))
            self.params[p + "bo"] = np.zeros((cfg.d_model,))

            # LayerNorm 2
            self.params[p + "ln2_gamma"] = np.ones((cfg.d_model,))
            self.params[p + "ln2_beta"] = np.zeros((cfg.d_model,))

            # Feed-Forward MLP
            self.params[p + "mlp_w1"] = np.random.randn(cfg.d_model, cfg.d_mlp) * np.sqrt(2.0 / (cfg.d_model + cfg.d_mlp))
            self.params[p + "mlp_b1"] = np.zeros((cfg.d_mlp,))
            self.params[p + "mlp_w2"] = np.random.randn(cfg.d_mlp, cfg.d_model) * np.sqrt(2.0 / (cfg.d_mlp + cfg.d_model))
            self.params[p + "mlp_b2"] = np.zeros((cfg.d_model,))

        # 3. Final LayerNorm & LM Head
        self.params["ln_f_gamma"] = np.ones((cfg.d_model,))
        self.params["ln_f_beta"] = np.zeros((cfg.d_model,))
        self.params["lm_head"] = np.random.randn(cfg.d_model, cfg.vocab_size) * scale

    @property
    def total_parameters(self) -> int:
        return sum(p.size for p in self.params.values())

    @property
    def model_size_mb(self) -> float:
        """Size of parameters in Megabytes (FP32)."""
        return (self.total_parameters * 4) / (1024 * 1024)

    # -------------------------------------------------------------
    # LayerNorm Forward & Backward
    # -------------------------------------------------------------
    @staticmethod
    def _layernorm_forward(x: np.ndarray, gamma: np.ndarray, beta: np.ndarray, eps: float = 1e-5):
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + eps)
        out = x_norm * gamma + beta
        cache = (x, x_norm, mean, var, gamma, eps)
        return out, cache

    @staticmethod
    def _layernorm_backward(dout: np.ndarray, cache: tuple):
        x, x_norm, mean, var, gamma, eps = cache
        N = x.shape[-1]
        std_inv = 1.0 / np.sqrt(var + eps)

        dgamma = np.sum(dout * x_norm, axis=(0, 1) if dout.ndim == 3 else 0)
        dbeta = np.sum(dout, axis=(0, 1) if dout.ndim == 3 else 0)

        dx_norm = dout * gamma
        dvar = np.sum(dx_norm * (x - mean) * -0.5 * (std_inv ** 3), axis=-1, keepdims=True)
        dmean = np.sum(dx_norm * -std_inv, axis=-1, keepdims=True) + dvar * np.mean(-2.0 * (x - mean), axis=-1, keepdims=True)
        dx = dx_norm * std_inv + dvar * 2.0 * (x - mean) / N + dmean / N
        return dx, dgamma, dbeta

    # -------------------------------------------------------------
    # Forward Pass
    # -------------------------------------------------------------
    def forward(self, input_ids: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Forward pass through the transformer.
        input_ids: shape (B, T)
        Returns:
            logits: shape (B, T, vocab_size)
            cache: forward activations for backprop
        """
        B, T = input_ids.shape
        cfg = self.config
        if T > cfg.max_seq_len:
            input_ids = input_ids[:, -cfg.max_seq_len:]
            T = cfg.max_seq_len

        # 1. Embeddings
        pos = np.arange(0, T)
        tok_emb = self.params["wte"][input_ids]     # (B, T, d_model)
        pos_emb = self.params["wpe"][pos]           # (T, d_model)
        x = tok_emb + pos_emb                       # (B, T, d_model)

        cache = {"input_ids": input_ids, "x_emb": x, "layers": []}

        # Causal Attention Mask
        # (1, 1, T, T): 0 for valid positions, -1e9 for future positions
        causal_mask = np.triu(np.ones((1, 1, T, T)) * -1e9, k=1)

        # 2. Iterate Transformer Layers
        for l in range(cfg.n_layers):
            p = f"layer_{l}."
            l_cache = {}

            # --- Pre-LN 1 ---
            ln1_out, l_cache["ln1"] = self._layernorm_forward(x, self.params[p + "ln1_gamma"], self.params[p + "ln1_beta"])

            # --- Multi-Head Self-Attention ---
            q = np.matmul(ln1_out, self.params[p + "wq"]) + self.params[p + "bq"]
            k = np.matmul(ln1_out, self.params[p + "wk"]) + self.params[p + "bk"]
            v = np.matmul(ln1_out, self.params[p + "wv"]) + self.params[p + "bv"]

            # Reshape to (B, H, T, d_head)
            q = q.reshape(B, T, cfg.n_heads, cfg.d_head).transpose(0, 2, 1, 3)
            k = k.reshape(B, T, cfg.n_heads, cfg.d_head).transpose(0, 2, 1, 3)
            v = v.reshape(B, T, cfg.n_heads, cfg.d_head).transpose(0, 2, 1, 3)

            # Scaled Dot-Product Attention
            scale = 1.0 / np.sqrt(cfg.d_head)
            scores = np.matmul(q, k.transpose(0, 1, 3, 2)) * scale  # (B, H, T, T)
            scores += causal_mask
            attn_weights = softmax(scores, axis=-1)

            context = np.matmul(attn_weights, v)  # (B, H, T, d_head)
            context = context.transpose(0, 2, 1, 3).reshape(B, T, cfg.d_model)

            attn_out = np.matmul(context, self.params[p + "wo"]) + self.params[p + "bo"]

            # Residual 1
            x = x + attn_out

            l_cache["mha"] = (ln1_out, q, k, v, attn_weights, context, causal_mask)

            # --- Pre-LN 2 ---
            ln2_out, l_cache["ln2"] = self._layernorm_forward(x, self.params[p + "ln2_gamma"], self.params[p + "ln2_beta"])

            # --- Feed-Forward MLP ---
            mlp_h1 = np.matmul(ln2_out, self.params[p + "mlp_w1"]) + self.params[p + "mlp_b1"]
            mlp_act = gelu(mlp_h1)
            mlp_out = np.matmul(mlp_act, self.params[p + "mlp_w2"]) + self.params[p + "mlp_b2"]

            # Residual 2
            x = x + mlp_out

            l_cache["mlp"] = (ln2_out, mlp_h1, mlp_act)
            cache["layers"].append(l_cache)

        # 3. Final LayerNorm & LM Head
        ln_f_out, cache["ln_f"] = self._layernorm_forward(x, self.params["ln_f_gamma"], self.params["ln_f_beta"])
        cache["ln_f_out"] = ln_f_out
        logits = np.matmul(ln_f_out, self.params["lm_head"])

        return logits, cache

    # -------------------------------------------------------------
    # Backward Pass (Analytical Matrix Calculus)
    # -------------------------------------------------------------
    def backward(self, dlogits: np.ndarray, cache: dict) -> Dict[str, np.ndarray]:
        """
        Backpropagation through all layers of the transformer.
        dlogits: shape (B, T, vocab_size)
        Returns:
            grads: dictionary of weight gradients matching self.params
        """
        grads: Dict[str, np.ndarray] = {}
        B, T, _ = dlogits.shape
        cfg = self.config

        # 1. LM Head Backward
        ln_f_out = cache["ln_f_out"]
        grads["lm_head"] = np.matmul(ln_f_out.reshape(-1, cfg.d_model).T, dlogits.reshape(-1, cfg.vocab_size))
        dx = np.matmul(dlogits, self.params["lm_head"].T)

        # Final LayerNorm Backward
        dx, grads["ln_f_gamma"], grads["ln_f_beta"] = self._layernorm_backward(dx, cache["ln_f"])

        # 2. Backprop through Transformer Layers in Reverse
        for l in reversed(range(cfg.n_layers)):
            p = f"layer_{l}."
            l_cache = cache["layers"][l]

            # --- MLP Backward ---
            ln2_out, mlp_h1, mlp_act = l_cache["mlp"]
            dmlp_out = dx  # from residual connection: d(x + mlp_out)/dmlp_out = 1

            grads[p + "mlp_w2"] = np.matmul(mlp_act.reshape(-1, cfg.d_mlp).T, dmlp_out.reshape(-1, cfg.d_model))
            grads[p + "mlp_b2"] = np.sum(dmlp_out, axis=(0, 1))

            dmlp_act = np.matmul(dmlp_out, self.params[p + "mlp_w2"].T)
            dmlp_h1 = dmlp_act * gelu_grad(mlp_h1)

            grads[p + "mlp_w1"] = np.matmul(ln2_out.reshape(-1, cfg.d_model).T, dmlp_h1.reshape(-1, cfg.d_mlp))
            grads[p + "mlp_b1"] = np.sum(dmlp_h1, axis=(0, 1))

            dln2_out = np.matmul(dmlp_h1, self.params[p + "mlp_w1"].T)

            # LN 2 Backward
            dln2_x, grads[p + "ln2_gamma"], grads[p + "ln2_beta"] = self._layernorm_backward(dln2_out, l_cache["ln2"])
            dx = dx + dln2_x  # residual accumulation

            # --- MHA Backward ---
            ln1_out, q, k, v, attn_weights, context, causal_mask = l_cache["mha"]
            dattn_out = dx

            grads[p + "wo"] = np.matmul(context.reshape(-1, cfg.d_model).T, dattn_out.reshape(-1, cfg.d_model))
            grads[p + "bo"] = np.sum(dattn_out, axis=(0, 1))

            dcontext = np.matmul(dattn_out, self.params[p + "wo"].T)
            dcontext = dcontext.reshape(B, T, cfg.n_heads, cfg.d_head).transpose(0, 2, 1, 3)

            # Context = Attn @ V -> dAttn = dContext @ V^T, dV = Attn^T @ dContext
            dattn_weights = np.matmul(dcontext, v.transpose(0, 1, 3, 2))
            dv = np.matmul(attn_weights.transpose(0, 1, 3, 2), dcontext)

            # Softmax backward
            dscores = attn_weights * (dattn_weights - np.sum(dattn_weights * attn_weights, axis=-1, keepdims=True))
            dscores = np.where(causal_mask < 0, 0.0, dscores)  # Zero out gradients for masked positions

            scale = 1.0 / np.sqrt(cfg.d_head)
            dscores = dscores * scale

            # Scores = Q @ K^T -> dQ = dScores @ K, dK = dScores^T @ Q
            dq = np.matmul(dscores, k)
            dk = np.matmul(dscores.transpose(0, 1, 3, 2), q)

            # Reshape back to (B, T, d_model)
            dq = dq.transpose(0, 2, 1, 3).reshape(B, T, cfg.d_model)
            dk = dk.transpose(0, 2, 1, 3).reshape(B, T, cfg.d_model)
            dv = dv.transpose(0, 2, 1, 3).reshape(B, T, cfg.d_model)

            flat_ln1 = ln1_out.reshape(-1, cfg.d_model)
            grads[p + "wq"] = np.matmul(flat_ln1.T, dq.reshape(-1, cfg.d_model))
            grads[p + "wk"] = np.matmul(flat_ln1.T, dk.reshape(-1, cfg.d_model))
            grads[p + "wv"] = np.matmul(flat_ln1.T, dv.reshape(-1, cfg.d_model))

            grads[p + "bq"] = np.sum(dq, axis=(0, 1))
            grads[p + "bk"] = np.sum(dk, axis=(0, 1))
            grads[p + "bv"] = np.sum(dv, axis=(0, 1))

            dln1_out = (
                np.matmul(dq, self.params[p + "wq"].T) +
                np.matmul(dk, self.params[p + "wk"].T) +
                np.matmul(dv, self.params[p + "wv"].T)
            )

            # LN 1 Backward
            dln1_x, grads[p + "ln1_gamma"], grads[p + "ln1_beta"] = self._layernorm_backward(dln1_out, l_cache["ln1"])
            dx = dx + dln1_x

        # 3. Embeddings Backward
        input_ids = cache["input_ids"]
        grads["wte"] = np.zeros_like(self.params["wte"])
        for b in range(B):
            for t in range(T):
                grads["wte"][input_ids[b, t]] += dx[b, t]

        grads["wpe"] = np.zeros_like(self.params["wpe"])
        grads["wpe"][:T] = np.sum(dx, axis=0)

        return grads

    # -------------------------------------------------------------
    # Loss Computation
    # -------------------------------------------------------------
    def compute_loss(self, logits: np.ndarray, targets: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Cross-entropy loss with stable log-sum-exp.
        logits: (B, T, vocab_size)
        targets: (B, T)
        """
        B, T, V = logits.shape
        flat_logits = logits.reshape(-1, V)
        flat_targets = targets.reshape(-1)

        # Softmax probabilities
        max_l = np.max(flat_logits, axis=-1, keepdims=True)
        exp_l = np.exp(flat_logits - max_l)
        probs = exp_l / (np.sum(exp_l, axis=-1, keepdims=True) + 1e-12)

        # Negative log-likelihood
        correct_probs = probs[np.arange(len(flat_targets)), flat_targets]
        loss = -np.mean(np.log(np.clip(correct_probs, 1e-12, 1.0)))

        # Gradient dLoss / dLogits = (probs - 1_y) / (B * T)
        dlogits = probs.copy()
        dlogits[np.arange(len(flat_targets)), flat_targets] -= 1.0
        dlogits = (dlogits / len(flat_targets)).reshape(B, T, V)

        return float(loss), dlogits

    # -------------------------------------------------------------
    # Autoregressive Generation & Sampling
    # -------------------------------------------------------------
    def generate(
        self,
        prompt_tokens: List[int],
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        top_k: int = 40,
        repetition_penalty: float = 1.15,
        eos_token_id: Optional[int] = None,
    ) -> List[int]:
        """Generate tokens autoregressively."""
        generated = list(prompt_tokens)

        for _ in range(max_new_tokens):
            context = generated[-self.config.max_seq_len:]
            input_ids = np.array([context], dtype=np.int32)

            logits, _ = self.forward(input_ids)
            next_logits = logits[0, -1, :].copy()

            # Repetition penalty
            if repetition_penalty != 1.0:
                recent = set(generated[-20:])
                for token_id in recent:
                    if next_logits[token_id] > 0:
                        next_logits[token_id] /= repetition_penalty
                    else:
                        next_logits[token_id] *= repetition_penalty

            # Temperature scaling
            temp = max(temperature, 1e-5)
            next_logits = next_logits / temp

            # Top-K filtering
            if top_k > 0 and top_k < len(next_logits):
                top_indices = np.argpartition(next_logits, -top_k)[-top_k:]
                mask = np.ones_like(next_logits, dtype=bool)
                mask[top_indices] = False
                next_logits[mask] = -1e9

            # Softmax to probabilities
            probs = softmax(next_logits)

            # Sample next token
            next_token = int(np.random.choice(len(probs), p=probs))
            generated.append(next_token)

            if eos_token_id is not None and next_token == eos_token_id:
                break

        return generated

    # -------------------------------------------------------------
    # Save & Load Model Weights
    # -------------------------------------------------------------
    def save_weights(self, filepath: str):
        """Save model parameters and configuration to compressed .npz file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        save_dict = dict(self.params)
        save_dict["__config__"] = np.array([str(self.config.to_dict())], dtype=object)
        np.savez_compressed(filepath, **save_dict)

    def load_weights(self, filepath: str):
        """Load model parameters from compressed .npz file."""
        data = np.load(filepath, allow_pickle=True)
        for k in self.params.keys():
            if k in data:
                self.params[k] = data[k]
        if "wpe" in self.params:
            self.config.max_seq_len = self.params["wpe"].shape[0]
