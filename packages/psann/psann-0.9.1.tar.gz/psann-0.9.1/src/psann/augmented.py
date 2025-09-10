from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn

from .utils import choose_device, seed_all


def _as_tensor(x, device, dtype=torch.float32):
    if isinstance(x, torch.Tensor):
        return x.to(device=device, dtype=dtype)
    return torch.from_numpy(np.asarray(x, dtype=np.float32)).to(device=device, dtype=dtype)


def _apply_transform(x: torch.Tensor, kind: str, eps: float = 1e-8) -> torch.Tensor:
    k = (kind or "identity").lower()
    if k == "identity":
        return x
    if k == "softmax":
        return torch.softmax(x, dim=-1)
    if k == "tanh":
        return torch.tanh(x)
    if k == "sigmoid":
        return torch.sigmoid(x)
    if k == "relu_norm":
        y = torch.relu(x) + eps
        return y / (y.sum(dim=-1, keepdim=True) + eps)
    raise ValueError(f"Unknown transform '{kind}'")


@dataclass
class PredictiveExtrasConfig:
    episode_length: int
    batch_episodes: int = 16
    primary_dim: int = 1            # first outputs used for reward
    extras_dim: int = 1             # last K outputs predict next extras
    primary_transform: str = "softmax"   # map primary logits -> allocations
    extras_transform: str = "tanh"       # bound extras in (-1,1)
    random_state: Optional[int] = None
    extras_l2: float = 0.0          # regularize extras magnitudes
    extras_smooth: float = 0.0      # regularize changes over time
    trans_cost: float = 0.0         # passed to reward if applicable


class PredictiveExtrasTrainer:
    """Episode trainer where the model predicts next-step extras.

    The model is assumed to output `primary_dim + extras_dim` values per step:
    - primary: used for reward (e.g., allocation logits, then transformed)
    - extras: transformed to produce next-step extras, concatenated to inputs

    You must provide observed feature episodes X of shape (N, F) and set the
    estimator to accept inputs of shape (F + extras_dim).
    """

    def __init__(
        self,
        model: nn.Module,
        reward_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        *,
        cfg: PredictiveExtrasConfig,
        device: torch.device | str = "auto",
        lr: float = 1e-3,
        optimizer: Optional[torch.optim.Optimizer] = None,
        grad_clip: Optional[float] = None,
        context_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        input_noise_std: Optional[float] = None,
        noise_decay: float = 1.0,
    ) -> None:
        self.model = model
        self.reward_fn = reward_fn
        self.cfg = cfg
        self.device = choose_device(device)
        self.model.to(self.device)
        self.opt = optimizer or torch.optim.Adam(self.model.parameters(), lr=lr)
        self.grad_clip = grad_clip
        self.context_extractor = context_extractor
        seed_all(self.cfg.random_state)
        self.input_noise_std = float(input_noise_std) if input_noise_std is not None else None
        self.noise_decay = float(noise_decay)
        self.history: list[dict] = []

    def _reset_state_if_any(self):
        if hasattr(self.model, "reset_state"):
            self.model.reset_state()

    def _commit_state_if_any(self):
        if hasattr(self.model, "commit_state_updates"):
            self.model.commit_state_updates()

    def _sample_batch(self, X_obs: np.ndarray, epoch_idx: Optional[int] = None) -> torch.Tensor:
        N = X_obs.shape[0]
        T = int(self.cfg.episode_length)
        if N < T:
            raise ValueError(f"Need at least {T} timesteps (got {N})")
        B = int(self.cfg.batch_episodes)
        starts = np.random.randint(0, N - T + 1, size=B)
        batch = np.stack([X_obs[s : s + T] for s in starts], axis=0).astype(np.float32)
        X_ep = _as_tensor(batch, self.device)
        if self.input_noise_std is not None and (self.noise_decay >= 0.0):
            factor = (self.noise_decay ** max(0, (epoch_idx or 0))) if epoch_idx is not None else 1.0
            X_ep = X_ep + torch.randn_like(X_ep) * (self.input_noise_std * factor)
        return X_ep

    def _rollout(self, X_ep: torch.Tensor, E0: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Rollout over an episode producing primary outputs and extras sequence.

        X_ep: (B,T,F)
        E0:   (B,K) initial extras; if None, zeros

        Returns primary (B,T,P) and extras_seq (B,T+1,K) where extras_seq[:,0]=E0.
        """
        B, T, F = X_ep.shape
        P = int(self.cfg.primary_dim)
        K = int(self.cfg.extras_dim)
        if E0 is None:
            E0 = torch.zeros((B, K), device=self.device)
        extras_seq = [E0]
        primaries = []
        self._reset_state_if_any()
        for t in range(T):
            xt = torch.cat([X_ep[:, t, :], extras_seq[-1]], dim=-1)
            yt = self.model(xt)
            if yt.ndim == 1:
                yt = yt[:, None]
            y_primary = yt[:, :P]
            y_extras = yt[:, P:P+K] if K > 0 else torch.empty((B, 0), device=yt.device, dtype=yt.dtype)
            primaries.append(_apply_transform(y_primary, self.cfg.primary_transform))
            next_E = _apply_transform(y_extras, self.cfg.extras_transform) if K > 0 else extras_seq[-1]
            extras_seq.append(next_E)
        self._commit_state_if_any()
        primary_bt = torch.stack(primaries, dim=1)  # (B,T,P)
        extras_bt = torch.stack(extras_seq, dim=1)  # (B,T+1,K)
        return primary_bt, extras_bt

    def train(self, X_obs: np.ndarray, *, epochs: int = 100, verbose: int = 1) -> None:
        self.model.train()
        import time
        for e in range(epochs):
            t0 = time.perf_counter()
            X_ep = self._sample_batch(X_obs, epoch_idx=e)  # (B,T,F)
            B, T, F = X_ep.shape
            # Initial extras as a learnable per-episode parameter
            E0 = torch.zeros((B, self.cfg.extras_dim), device=self.device, requires_grad=True)
            primary, extras = self._rollout(X_ep, E0=E0)
            # Build context for reward
            ctx = self.context_extractor(X_ep) if self.context_extractor is not None else X_ep
            # If reward expects prices (B,T,M), require dim match
            rewards = self.reward_fn(primary, ctx)  # (B,)
            loss = -rewards.mean()
            # Regularize extras
            if self.cfg.extras_l2 > 0 and self.cfg.extras_dim > 0:
                loss = loss + self.cfg.extras_l2 * extras[:, 1:, :].pow(2).mean()
            if self.cfg.extras_smooth > 0 and self.cfg.extras_dim > 0:
                dE = extras[:, 1:, :] - extras[:, :-1, :]
                loss = loss + self.cfg.extras_smooth * dE.pow(2).mean()

            self.opt.zero_grad()
            loss.backward()
            if self.grad_clip is not None and self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            # Also backprop into E0, but we do not step it via optimizer
            with torch.no_grad():
                E0 -= 0.1 * E0.grad if E0.grad is not None else 0.0
            self.opt.step()
            dt = time.perf_counter() - t0
            rec = {"epoch": len(self.history) + 1, "train_reward": float(rewards.mean().item()), "time_s": float(dt)}
            self.history.append(rec)
            if verbose:
                print(f"[PredictiveExtras] epoch {e+1}/{epochs} reward={rec['train_reward']:.6f}")

    @torch.no_grad()
    def infer_series(self, X_obs: np.ndarray, *, E0: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Roll out predictions and extras over the full series.

        Returns (primary, extras) as numpy arrays with shapes (N, P) and (N+1, K).
        """
        self.model.eval()
        X = _as_tensor(X_obs, self.device)
        if X.ndim != 2:
            raise ValueError("X_obs must be (N, F) for series inference")
        N, F = X.shape
        P = int(self.cfg.primary_dim)
        K = int(self.cfg.extras_dim)
        if E0 is None:
            e0 = torch.zeros((1, K), device=self.device)
        else:
            e0 = _as_tensor(E0, self.device).reshape(1, K)
        prim = []
        extras = [e0[0]]
        self._reset_state_if_any()
        for t in range(N):
            xt = torch.cat([X[t : t + 1], extras[-1].reshape(1, -1)], dim=-1)
            yt = self.model(xt)
            y_primary = yt[:, :P]
            prim.append(_apply_transform(y_primary, self.cfg.primary_transform)[0])
            if K > 0:
                y_extras = yt[:, P:P+K]
                next_E = _apply_transform(y_extras, self.cfg.extras_transform)[0]
            else:
                next_E = extras[-1]
            extras.append(next_E)
        self._commit_state_if_any()
        prim_np = torch.stack(prim, dim=0).cpu().numpy()
        extras_np = torch.stack(extras, dim=0).cpu().numpy()
        return prim_np, extras_np

    @torch.no_grad()
    def evaluate_reward(self, X_obs: np.ndarray, *, n_batches: int = 8) -> float:
        self.model.eval()
        vals = []
        for _ in range(n_batches):
            X_ep = self._sample_batch(X_obs)
            B, T, F = X_ep.shape
            E0 = torch.zeros((B, self.cfg.extras_dim), device=self.device)
            primary, _ = self._rollout(X_ep, E0=E0)
            ctx = self.context_extractor(X_ep) if self.context_extractor is not None else X_ep
            # Reward function is expected to capture any extra kwargs (e.g., trans_cost)
            vals.append(float(self.reward_fn(primary, ctx).mean().item()))
        return float(np.mean(vals))


def make_predictive_extras_trainer_from_estimator(
    est, *, cfg: PredictiveExtrasConfig, reward_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor], device: torch.device | str = "auto", lr: float = 1e-3, context_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
) -> PredictiveExtrasTrainer:
    if not hasattr(est, "model_"):
        raise RuntimeError("Estimator not fitted; call fit() first.")
    return PredictiveExtrasTrainer(est.model_, reward_fn, cfg=cfg, device=device, lr=lr, context_extractor=context_extractor)
