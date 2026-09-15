"""Vectorized AdamW Optimizer with gradient clipping and weight decay."""
import numpy as np
from typing import Dict, Optional

class AdamW:
    def __init__(
        self,
        params: Dict[str, np.ndarray],
        lr: float = 1e-3,
        betas: tuple = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01,
        clip_grad: float = 1.0,
    ):
        self.params = params
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.clip_grad = clip_grad

        # State moments
        self.m: Dict[str, np.ndarray] = {k: np.zeros_like(v) for k, v in params.items()}
        self.v: Dict[str, np.ndarray] = {k: np.zeros_like(v) for k, v in params.items()}
        self.t = 0

    def step(self, grads: Dict[str, np.ndarray], custom_lr: Optional[float] = None):
        """Perform a single optimization step using analytical gradients."""
        self.t += 1
        lr = custom_lr if custom_lr is not None else self.lr

        # Global gradient clipping
        total_norm_sq = 0.0
        for g in grads.values():
            total_norm_sq += np.sum(g ** 2)
        total_norm = np.sqrt(total_norm_sq)

        scale = 1.0
        if self.clip_grad > 0 and total_norm > self.clip_grad:
            scale = self.clip_grad / (total_norm + 1e-6)

        # Bias correction terms
        beta1_t = self.beta1 ** self.t
        beta2_t = self.beta2 ** self.t
        alpha_t = lr * np.sqrt(1.0 - beta2_t) / (1.0 - beta1_t)

        for name, param in self.params.items():
            if name not in grads:
                continue

            grad = grads[name] * scale

            # Update biased 1st moment vector
            self.m[name] = self.beta1 * self.m[name] + (1.0 - self.beta1) * grad
            # Update biased 2nd moment vector
            self.v[name] = self.beta2 * self.v[name] + (1.0 - self.beta2) * (grad ** 2)

            # AdamW weight decay (applied directly to weights, not gradients)
            if self.weight_decay > 0 and "norm" not in name and "b" not in name:
                param -= lr * self.weight_decay * param

            # Parameter update
            param -= alpha_t * self.m[name] / (np.sqrt(self.v[name]) + self.eps)
