from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn

from .nn import PSANNNet, WithPreprocessor
from .utils import choose_device, seed_all
from .tokenizer import BaseTokenizer, SimpleWordTokenizer
from .embeddings import SineTokenEmbedder


@dataclass
class LMConfig:
    embedding_dim: int = 64
    extras_dim: int = 0
    episode_length: int = 64
    batch_episodes: int = 32
    random_state: Optional[int] = None
    # Perplexity monitoring
    ppx_every: int = 0           # 0 disables periodic perplexity
    ppx_temperature: float = 1.0
    # Curriculum learning over token stream (progressively unlock prefix)
    curriculum_type: Optional[str] = None  # 'progressive_span' or None
    curriculum_warmup_epochs: int = 10     # epochs to reach full coverage
    curriculum_min_frac: float = 0.1       # starting fraction of stream
    curriculum_max_frac: float = 1.0       # final fraction


class LMExtrasTrainer:
    """Episode trainer for next-token prediction with extras.

    Model maps [emb_t, extras_t] -> [emb_{t+1}, extras_{t+1}].
    Loss: MSE between predicted emb_{t+1} and target emb_{t+1} (averaged over episode),
    plus optional regularizers on extras.
    """

    def __init__(
        self,
        model: nn.Module,
        embedder: SineTokenEmbedder,
        *,
        cfg: LMConfig,
        device: torch.device | str = "auto",
        lr: float = 1e-3,
        optimizer: Optional[torch.optim.Optimizer] = None,
        grad_clip: Optional[float] = None,
        input_noise_std: Optional[float] = None,
        noise_decay: float = 1.0,
    ) -> None:
        self.model = model
        self.embedder = embedder
        self.cfg = cfg
        self.device = choose_device(device)
        self.model.to(self.device)
        # Ensure embedder uses same device as model
        try:
            self.embedder.to(self.device)
        except AttributeError:
            pass
        params = list(self.model.parameters()) + list(getattr(self.embedder, 'parameters', lambda: [])())
        self.opt = optimizer or torch.optim.Adam(params, lr=lr)
        self.grad_clip = grad_clip
        seed_all(self.cfg.random_state)
        self.input_noise_std = float(input_noise_std) if input_noise_std is not None else None
        self.noise_decay = float(noise_decay)
        self.history: List[dict] = []

    def _sample_batch(self, token_ids: np.ndarray, epoch_idx: Optional[int] = None) -> torch.Tensor:
        N = token_ids.shape[0]
        T = int(self.cfg.episode_length)
        if N < T + 1:
            raise ValueError(f"Need at least {T+1} tokens for LM episodes (got {N})")
        B = int(self.cfg.batch_episodes)
        # Curriculum: limit the max start index by a fraction of the stream
        hi = N - (T + 1)
        start_hi = hi
        if self.cfg.curriculum_type == "progressive_span" and epoch_idx is not None and self.cfg.curriculum_warmup_epochs > 0:
            frac0 = max(0.0, min(1.0, float(self.cfg.curriculum_min_frac)))
            frac1 = max(0.0, min(1.0, float(self.cfg.curriculum_max_frac)))
            alpha = max(0.0, min(1.0, epoch_idx / max(1, int(self.cfg.curriculum_warmup_epochs))))
            frac = frac0 + (frac1 - frac0) * alpha
            start_hi = max(0, int(frac * hi))
        start_hi = max(0, start_hi)
        starts = np.random.randint(0, max(1, start_hi + 1), size=B)
        batch = np.stack([token_ids[s : s + T + 1] for s in starts], axis=0).astype(np.int64)
        X_ids = torch.from_numpy(batch).to(self.device)  # (B, T+1)
        return X_ids

    def _rollout(self, X_ids: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Roll out over episode returning predicted embeddings and targets.

        X_ids: (B, T+1) token ids; for t in 0..T-1, predict emb(x_{t+1}) from x_t.
        Returns: (pred_emb: (B,T,D), tgt_emb: (B,T,D), next_ids: (B,T))
        """
        B, Tp1 = X_ids.shape
        T = Tp1 - 1
        D = int(self.embedder.embedding_dim)
        K = int(self.cfg.extras_dim)
        # Prepare extras
        extras_t = torch.zeros((B, K), dtype=torch.float32, device=self.device) if K > 0 else None
        preds = []
        tgts = []
        next_ids_list = []
        for t in range(T):
            x_t = X_ids[:, t]
            x_tp1 = X_ids[:, t + 1]
            emb_t = self.embedder(x_t)  # (B,D)
            if self.input_noise_std is not None and self.noise_decay >= 0.0:
                factor = (self.noise_decay ** max(0, (t)))
                emb_t = emb_t + torch.randn_like(emb_t) * (self.input_noise_std * factor)
            if K > 0:
                inp = torch.cat([emb_t, extras_t], dim=-1)
            else:
                inp = emb_t
            y = self.model(inp)
            y_emb = y[:, :D]
            preds.append(y_emb)
            tgt_emb = self.embedder(x_tp1).detach()  # fixed targets unless embedder is meant to be trainable separately
            tgts.append(tgt_emb)
            next_ids_list.append(x_tp1)
            if K > 0:
                extras_t = y[:, D : D + K].detach()  # feedforward predicted extras
        pred_bt = torch.stack(preds, dim=1)
        tgt_bt = torch.stack(tgts, dim=1)
        next_ids = torch.stack(next_ids_list, dim=1)
        return pred_bt, tgt_bt, next_ids

    @torch.no_grad()
    def _batch_perplexity(self, pred: torch.Tensor, next_ids: torch.Tensor) -> float:
        """Compute perplexity using cosine-sim softmax over vocab embeddings.

        pred: (B,T,D), next_ids: (B,T)
        """
        D = pred.shape[-1]
        # Rebuild table if embedder is trainable so it reflects latest params
        try:
            if any(p.requires_grad for p in self.embedder.parameters()):
                self.embedder._rebuild_table()
        except Exception:
            pass
        table = self.embedder.embedding_matrix()  # (V,D)
        if table.numel() == 0:
            return float('nan')
        # Normalize
        tn = table / (table.norm(p=2, dim=1, keepdim=True) + 1e-8)
        y = pred.reshape(-1, D)
        yn = y / (y.norm(p=2, dim=1, keepdim=True) + 1e-8)
        logits = torch.matmul(yn, tn.T) / max(1e-6, float(self.cfg.ppx_temperature))  # (B*T, V)
        # cross-entropy to true next token ids
        tgt = next_ids.reshape(-1).to(device=logits.device, dtype=torch.long)
        log_probs = logits - torch.logsumexp(logits, dim=1, keepdim=True)
        nll = -log_probs[torch.arange(logits.shape[0]), tgt].mean()
        ppl = torch.exp(nll).item()
        return float(ppl)

    def train(self, token_ids: np.ndarray, *, epochs: int = 50, verbose: int = 1) -> None:
        self.model.train()
        try:
            self.embedder.train()
        except Exception:
            pass
        import time
        for e in range(epochs):
            t0 = time.perf_counter()
            X_ids = self._sample_batch(token_ids, epoch_idx=e)
            pred, tgt, next_ids = self._rollout(X_ids)
            loss = torch.mean((pred - tgt) ** 2)
            self.opt.zero_grad()
            loss.backward()
            if self.grad_clip is not None and self.grad_clip > 0:
                params = list(self.model.parameters()) + list(getattr(self.embedder, 'parameters', lambda: [])())
                torch.nn.utils.clip_grad_norm_(params, self.grad_clip)
            self.opt.step()
            dt = time.perf_counter() - t0
            rec = {"epoch": len(self.history) + 1, "train_mse": float(loss.item()), "time_s": float(dt)}
            if int(self.cfg.ppx_every) > 0 and ((e + 1) % int(self.cfg.ppx_every) == 0):
                rec["perplexity"] = self._batch_perplexity(pred.detach(), next_ids.detach())
            self.history.append(rec)
            if verbose:
                msg = f"[LM] epoch {e+1}/{epochs} mse={rec['train_mse']:.6f}"
                if "perplexity" in rec:
                    msg += f" ppx={rec['perplexity']:.3f}"
                print(msg)


class PSANNLanguageModel:
    """PSANN-LM: Simple language model using PSANN for next-token embedding prediction.

    Pipeline:
    - Tokenize text into ids via provided or internal tokenizer.
    - Map ids to sinusoidal embeddings via SineTokenEmbedder (pretrained or internal).
    - Train PSANNNet to predict next embedding given current embedding (+ extras).
    - Predict: decode next token via nearest neighbor in embedding space.
    - Generate: iteratively predict tokens and decode.
    """

    def __init__(
        self,
        *,
        tokenizer: Optional[BaseTokenizer] = None,
        embedder: Optional[SineTokenEmbedder] = None,
        lm_cfg: Optional[LMConfig] = None,
        hidden_layers: int = 2,
        hidden_width: int = 128,
        activation_type: str = "psann",
        w0: float = 30.0,
        device: torch.device | str = "auto",
        random_state: Optional[int] = None,
    ) -> None:
        self.tokenizer = tokenizer or SimpleWordTokenizer()
        self.embedder = embedder
        self.cfg = lm_cfg or LMConfig()
        self.hidden_layers = int(hidden_layers)
        self.hidden_width = int(hidden_width)
        self.activation_type = activation_type
        self.w0 = float(w0)
        self.device = choose_device(device)
        self.random_state = random_state
        self.model_: Optional[nn.Module] = None
        self.trainer_: Optional[LMExtrasTrainer] = None
        self.history: List[dict] = []

    def _build_model(self, vocab_size: int) -> None:
        seed_all(self.random_state)
        if self.embedder is None:
            self.embedder = SineTokenEmbedder(self.cfg.embedding_dim)
        self.embedder.set_vocab_size(vocab_size)
        D = int(self.cfg.embedding_dim)
        K = int(self.cfg.extras_dim)
        core = PSANNNet(
            D + K,
            D + K,
            hidden_layers=self.hidden_layers,
            hidden_width=self.hidden_width,
            act_kw={},
            state_cfg=None,
            activation_type=self.activation_type,
            w0=self.w0,
        )
        self.model_ = WithPreprocessor(None, core).to(self.device)
        # Keep embedder on the same device for consistent ops
        try:
            assert self.embedder is not None
            self.embedder.to(self.device)
        except Exception:
            pass

    def _concat_corpus(self, corpus: Iterable[str]) -> np.ndarray:
        ids: List[int] = []
        for text in corpus:
            ids.extend(self.tokenizer.encode(text, add_bos=True, add_eos=True))
        return np.asarray(ids, dtype=np.int64)

    def fit(
        self,
        corpus: List[str],
        *,
        epochs: int = 50,
        lr: float = 1e-3,
        noisy: Optional[float] = None,
        verbose: int = 1,
        # Perplexity and curriculum controls (override LMConfig if provided)
        ppx_every: Optional[int] = None,
        ppx_temperature: Optional[float] = None,
        curriculum_type: Optional[str] = None,
        curriculum_warmup_epochs: Optional[int] = None,
        curriculum_min_frac: Optional[float] = None,
        curriculum_max_frac: Optional[float] = None,
    ) -> "PSANNLanguageModel":
        # Build tokenizer and vocab
        self.tokenizer.fit(corpus)
        vocab_size = self.tokenizer.vocab_size
        # Build model and embedder
        self._build_model(vocab_size)
        assert self.embedder is not None and self.model_ is not None
        # Trainer
        self.trainer_ = LMExtrasTrainer(
            self.model_,
            self.embedder,
            cfg=self.cfg,
            device=self.device,
            lr=lr,
            input_noise_std=noisy,
        )
        # Apply any overrides to config
        if ppx_every is not None:
            self.cfg.ppx_every = int(ppx_every)
        if ppx_temperature is not None:
            self.cfg.ppx_temperature = float(ppx_temperature)
        if curriculum_type is not None:
            self.cfg.curriculum_type = str(curriculum_type)
        if curriculum_warmup_epochs is not None:
            self.cfg.curriculum_warmup_epochs = int(curriculum_warmup_epochs)
        if curriculum_min_frac is not None:
            self.cfg.curriculum_min_frac = float(curriculum_min_frac)
        if curriculum_max_frac is not None:
            self.cfg.curriculum_max_frac = float(curriculum_max_frac)
        token_ids = self._concat_corpus(corpus)
        self.trainer_.train(token_ids, epochs=int(epochs), verbose=int(verbose))
        self.history = getattr(self.trainer_, "history", [])
        return self

    @torch.no_grad()
    def predict(self, text: str, *, return_embedding: bool = False) -> str | np.ndarray:
        if self.model_ is None or self.embedder is None:
            raise RuntimeError("Model not fitted")
        ids = self.tokenizer.encode(text, add_bos=True, add_eos=False)
        if len(ids) == 0:
            return ""
        last = torch.tensor([ids[-1]], dtype=torch.long, device=self.device)
        emb = self.embedder(last)  # (1,D)
        K = int(self.cfg.extras_dim)
        if K > 0:
            inp = torch.cat([emb, torch.zeros((1, K), device=self.device)], dim=-1)
        else:
            inp = emb
        y = self.model_(inp)
        D = int(self.cfg.embedding_dim)
        y_emb = y[:, :D]
        if return_embedding:
            return y_emb[0].detach().cpu().numpy()
        # Nearest neighbor in embedding space by cosine similarity
        # Rebuild table if embedder is trainable so it reflects latest params
        try:
            if any(p.requires_grad for p in self.embedder.parameters()):
                self.embedder._rebuild_table()
        except Exception:
            pass
        table = self.embedder.embedding_matrix()  # (V,D)
        v = y_emb[0]
        vn = v / (v.norm(p=2) + 1e-8)
        tn = table / (table.norm(p=2, dim=1, keepdim=True) + 1e-8)
        sim = torch.matmul(tn, vn)
        idx = int(torch.argmax(sim).item())
        return self.tokenizer.decode([idx])

    @torch.no_grad()
    def generate(self, prompt: str, *, max_tokens: int = 20) -> str:
        if self.model_ is None or self.embedder is None:
            raise RuntimeError("Model not fitted")
        ids = self.tokenizer.encode(prompt, add_bos=True, add_eos=False)
        if len(ids) == 0:
            return prompt
        K = int(self.cfg.extras_dim)
        extras_t = torch.zeros((1, K), device=self.device) if K > 0 else None
        for _ in range(int(max_tokens)):
            last_id = torch.tensor([ids[-1]], dtype=torch.long, device=self.device)
            emb = self.embedder(last_id)
            if K > 0 and extras_t is not None:
                inp = torch.cat([emb, extras_t], dim=-1)
            else:
                inp = emb
            y = self.model_(inp)
            D = int(self.cfg.embedding_dim)
            y_emb = y[:, :D]
            if K > 0:
                extras_t = y[:, D : D + K]
            # Nearest neighbor decoding
            # Ensure table is up-to-date if embedder is trainable
            try:
                if any(p.requires_grad for p in self.embedder.parameters()):
                    self.embedder._rebuild_table()
            except Exception:
                pass
            table = self.embedder.embedding_matrix()
            vn = y_emb[0] / (y_emb[0].norm(p=2) + 1e-8)
            tn = table / (table.norm(p=2, dim=1, keepdim=True) + 1e-8)
            sim = torch.matmul(tn, vn)
            idx = int(torch.argmax(sim).item())
            ids.append(idx)
            # Stop on EOS if present in vocab
            try:
                eos_id = self.tokenizer._tok2id.get(SimpleWordTokenizer.EOS, -1)  # type: ignore[attr-defined]
            except Exception:
                eos_id = -1
            if idx == eos_id:
                break
        return self.tokenizer.decode(ids)

    # Convenience alias
    def gen(self, prompt: str, *, max_tokens: int = 20) -> str:
        return self.generate(prompt, max_tokens=max_tokens)

    # ------------------------------ Persistence ------------------------------
    def save(self, path: str) -> None:
        if self.model_ is None or self.embedder is None:
            raise RuntimeError("Model is not fitted; call fit() before save().")
        # Tokenizer serialization (supports SimpleWordTokenizer)
        tok_meta = {"type": self.tokenizer.__class__.__name__}
        if isinstance(self.tokenizer, SimpleWordTokenizer):
            tok_meta.update({
                "lowercase": bool(getattr(self.tokenizer, "lowercase", True)),
                "max_vocab": getattr(self.tokenizer, "max_vocab", None),
                "id2tok": list(getattr(self.tokenizer, "_id2tok", [])),
            })
        else:
            # Best-effort; caller can rebuild tokenizer externally if custom
            tok_meta.update({"note": "Unsupported tokenizer type; only type name saved."})

        # Embedder serialization
        emb_meta = {"type": self.embedder.__class__.__name__}
        if isinstance(self.embedder, SineTokenEmbedder):
            emb_meta.update({
                "embedding_dim": int(self.embedder.embedding_dim),
                "base": float(getattr(self.embedder, "base", 10000.0)),
                "scale": float(getattr(self.embedder, "scale", 1.0)),
                "trainable": bool(getattr(self.embedder, "trainable", False)),
            })
            emb_state = self.embedder.state_dict()
        else:
            emb_state = self.embedder.state_dict()

        payload = {
            "class": "PSANNLanguageModel",
            "params": {
                "hidden_layers": self.hidden_layers,
                "hidden_width": self.hidden_width,
                "activation_type": self.activation_type,
                "w0": self.w0,
                "random_state": self.random_state,
            },
            "cfg": {
                "embedding_dim": int(self.cfg.embedding_dim),
                "extras_dim": int(self.cfg.extras_dim),
                "episode_length": int(self.cfg.episode_length),
                "batch_episodes": int(self.cfg.batch_episodes),
                "random_state": self.cfg.random_state,
                "ppx_every": int(getattr(self.cfg, "ppx_every", 0)),
                "ppx_temperature": float(getattr(self.cfg, "ppx_temperature", 1.0)),
                "curriculum_type": getattr(self.cfg, "curriculum_type", None),
                "curriculum_warmup_epochs": int(getattr(self.cfg, "curriculum_warmup_epochs", 10)),
                "curriculum_min_frac": float(getattr(self.cfg, "curriculum_min_frac", 0.1)),
                "curriculum_max_frac": float(getattr(self.cfg, "curriculum_max_frac", 1.0)),
            },
            "tokenizer": tok_meta,
            "embedder": emb_meta,
            "embedder_state": emb_state,
            "model_state": self.model_.state_dict(),
            "meta": {"version": 1},
        }
        torch.save(payload, path)

    @classmethod
    def load(cls, path: str, map_location: Optional[str | torch.device] = None) -> "PSANNLanguageModel":
        payload = torch.load(path, map_location=map_location or "cpu")
        params = payload.get("params", {})
        cfg_d = payload.get("cfg", {})
        tok_meta = payload.get("tokenizer", {})
        emb_meta = payload.get("embedder", {})
        emb_state = payload.get("embedder_state", {})
        model_state = payload.get("model_state", {})

        # Rebuild tokenizer
        tok_type = tok_meta.get("type", "")
        if tok_type == "SimpleWordTokenizer":
            tok = SimpleWordTokenizer(lowercase=bool(tok_meta.get("lowercase", True)), max_vocab=tok_meta.get("max_vocab", None))
            id2tok = list(tok_meta.get("id2tok", []))
            if id2tok:
                tok._id2tok = id2tok  # type: ignore[attr-defined]
                tok._tok2id = {w: i for i, w in enumerate(id2tok)}  # type: ignore[attr-defined]
        else:
            # Fallback: empty tokenizer; user may replace later
            tok = SimpleWordTokenizer()

        # Rebuild embedder
        emb_type = emb_meta.get("type", "")
        if emb_type == "SineTokenEmbedder":
            emb = SineTokenEmbedder(
                int(emb_meta.get("embedding_dim", cfg_d.get("embedding_dim", 64))),
                base=float(emb_meta.get("base", 10000.0)),
                scale=float(emb_meta.get("scale", 1.0)),
                trainable=bool(emb_meta.get("trainable", False)),
            )
            emb.load_state_dict(emb_state)
        else:
            # Unknown embedder; best-effort
            emb = SineTokenEmbedder(int(cfg_d.get("embedding_dim", 64)))

        # Construct LM
        cfg = LMConfig(
            embedding_dim=int(cfg_d.get("embedding_dim", 64)),
            extras_dim=int(cfg_d.get("extras_dim", 0)),
            episode_length=int(cfg_d.get("episode_length", 64)),
            batch_episodes=int(cfg_d.get("batch_episodes", 32)),
            random_state=cfg_d.get("random_state", None),
            ppx_every=int(cfg_d.get("ppx_every", 0)),
            ppx_temperature=float(cfg_d.get("ppx_temperature", 1.0)),
            curriculum_type=cfg_d.get("curriculum_type", None),
            curriculum_warmup_epochs=int(cfg_d.get("curriculum_warmup_epochs", 10)),
            curriculum_min_frac=float(cfg_d.get("curriculum_min_frac", 0.1)),
            curriculum_max_frac=float(cfg_d.get("curriculum_max_frac", 1.0)),
        )
        obj = cls(
            tokenizer=tok,
            embedder=emb,
            lm_cfg=cfg,
            hidden_layers=int(params.get("hidden_layers", 2)),
            hidden_width=int(params.get("hidden_width", 128)),
            activation_type=str(params.get("activation_type", "psann")),
            w0=float(params.get("w0", 30.0)),
            device=map_location or "cpu",
            random_state=params.get("random_state", None),
        )
        # Build model and load weights
        vocab_size = tok.vocab_size
        obj._build_model(vocab_size)
        assert obj.model_ is not None
        obj.model_.load_state_dict(model_state)
        # Ensure embedder knows vocab size for nearest-neighbor table
        assert obj.embedder is not None
        obj.embedder.set_vocab_size(vocab_size)
        return obj
