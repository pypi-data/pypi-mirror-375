from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Tuple, Callable, Union
import warnings

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

try:  # Optional scikit-learn import for API compatibility
    from sklearn.base import BaseEstimator, RegressorMixin  # type: ignore
    from sklearn.metrics import r2_score as _sk_r2_score  # type: ignore
except Exception:  # Fallbacks if sklearn isn't installed at runtime
    class BaseEstimator:  # minimal stub
        def get_params(self, deep: bool = True):
            # Return non-private, non-callable attributes
            params = {}
            for k, v in self.__dict__.items():
                if k.endswith("_"):
                    continue
                if not k.startswith("_") and not callable(v):
                    params[k] = v
            return params

        def set_params(self, **params):
            for k, v in params.items():
                setattr(self, k, v)
            return self

    class RegressorMixin:
        pass

    def _sk_r2_score(y_true, y_pred):
            y_true = np.asarray(y_true)
            y_pred = np.asarray(y_pred)
            u = ((y_true - y_pred) ** 2).sum()
            v = ((y_true - y_true.mean()) ** 2).sum()
            return 1.0 - (u / v if v != 0 else np.nan)

from .nn import PSANNNet, WithPreprocessor
from .conv import PSANNConv1dNet, PSANNConv2dNet, PSANNConv3dNet
from .utils import choose_device, seed_all
from .types import ActivationConfig


class PSANNRegressor(BaseEstimator, RegressorMixin):
    """Sklearn-style regressor wrapper around a PSANN network (PyTorch).

    Parameters mirror the README's proposed API.
    """

    def __init__(
        self,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 64,
        epochs: int = 200,
        batch_size: int = 128,
        lr: float = 1e-3,
        optimizer: str = "adam",
        weight_decay: float = 0.0,
        activation: Optional[ActivationConfig] = None,
        device: str | torch.device = "auto",
        random_state: Optional[int] = None,
        early_stopping: bool = False,
        patience: int = 20,
        num_workers: int = 0,
        loss: Any = "mse",
        loss_params: Optional[Dict[str, Any]] = None,
        loss_reduction: str = "mean",
        w0: float = 30.0,
        preserve_shape: bool = False,
        data_format: str = "channels_first",
        conv_kernel_size: int = 1,
        per_element: bool = False,
        activation_type: str = "psann",
        stateful: bool = False,
        state: Optional[Dict[str, Any]] = None,
        state_reset: str = "batch",  # 'batch' | 'epoch' | 'none'
        stream_lr: Optional[float] = None,
        output_shape: Optional[Tuple[int, ...]] = None,
        lsm: Optional[Any] = None,
        lsm_train: bool = False,
        lsm_pretrain_epochs: int = 0,
        lsm_lr: Optional[float] = None,
        extras: int = 0,
        warm_start: bool = False,
        scaler: Optional[Union[str, Any]] = None,
        scaler_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.hidden_layers = hidden_layers
        self.hidden_width = hidden_width
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.optimizer = optimizer
        self.weight_decay = weight_decay
        self.activation = activation or {}
        self.device = device
        self.random_state = random_state
        self.early_stopping = early_stopping
        self.patience = patience
        self.num_workers = num_workers
        self.loss = loss
        self.loss_params = loss_params
        self.loss_reduction = loss_reduction
        self.w0 = w0
        self.preserve_shape = preserve_shape
        self.data_format = data_format
        self.conv_kernel_size = conv_kernel_size
        self.per_element = per_element
        self.activation_type = activation_type
        self.stateful = stateful
        self.state = state or None
        self.state_reset = state_reset
        self.stream_lr = stream_lr
        self.output_shape = output_shape
        self.lsm = lsm
        self.lsm_train = lsm_train
        self.lsm_pretrain_epochs = lsm_pretrain_epochs
        self.lsm_lr = lsm_lr
        self.extras = int(extras)
        self.warm_start = bool(warm_start)
        # Optional input scaler (minmax/standard or custom object with fit/transform)
        self.scaler = scaler
        self.scaler_params = scaler_params or None

        # Fitted scaler state (set during fit)
        self._scaler_kind_: Optional[str] = None
        self._scaler_state_: Optional[Dict[str, Any]] = None

    # ------------------------- Scaling helpers -------------------------
    def _make_internal_scaler(self) -> Optional[Dict[str, Any]]:
        kind = self.scaler
        if kind is None:
            return None
        if isinstance(kind, str):
            key = kind.lower()
            if key not in {"standard", "minmax"}:
                raise ValueError("Unsupported scaler string. Use 'standard', 'minmax', or provide an object with fit/transform.")
            return {"type": key, "state": {}}
        # Custom object: must implement fit/transform; inverse_transform optional
        if not hasattr(kind, "fit") or not hasattr(kind, "transform"):
            raise ValueError("Custom scaler must implement fit(X) and transform(X). Optional inverse_transform(X).")
        return {"type": "custom", "obj": kind}

    def _scaler_fit_update(self, X2d: np.ndarray) -> Optional[Callable[[np.ndarray], np.ndarray]]:
        """Fit or update scaler on 2D array and return a transform function.

        - For built-in scalers, supports incremental update when warm_start=True.
        - For custom object, calls .fit on first time, else attempts partial_fit if available, else refit on concat.
        """
        if self.scaler is None:
            self._scaler_kind_ = None
            self._scaler_state_ = None
            return None
        spec = getattr(self, "_scaler_spec_", None)
        if spec is None:
            spec = self._make_internal_scaler()
            self._scaler_spec_ = spec
        if spec is None:
            self._scaler_kind_ = None
            self._scaler_state_ = None
            return None

        if spec.get("type") == "standard":
            self._scaler_kind_ = "standard"
            st = self._scaler_state_ or {"n": 0, "mean": None, "M2": None}
            n0 = int(st["n"])
            X = np.asarray(X2d, dtype=np.float32)
            # Welford online update per feature
            if n0 == 0:
                mean = X.mean(axis=0)
                diff = X - mean
                M2 = (diff * diff).sum(axis=0)
                n = X.shape[0]
            else:
                mean0 = st["mean"]
                M20 = st["M2"]
                n = n0 + X.shape[0]
                delta = X.mean(axis=0) - mean0
                mean = (mean0 * n0 + X.sum(axis=0)) / n
                # Update M2 across batches: combine variances
                # M2_total = M2_a + M2_b + delta^2 * n_a * n_b / n_total
                M2a = M20
                xa = n0
                xb = X.shape[0]
                X_centered = X - X.mean(axis=0)
                M2b = (X_centered * X_centered).sum(axis=0)
                M2 = M2a + M2b + (delta * delta) * (xa * xb) / max(n, 1)
            self._scaler_state_ = {"n": int(n), "mean": mean, "M2": M2}

            def _xfm(Z: np.ndarray) -> np.ndarray:
                st2 = self._scaler_state_
                assert st2 is not None
                mean2 = st2["mean"]
                var = st2["M2"] / max(st2["n"], 1)
                std = np.sqrt(np.maximum(var, 1e-8)).astype(np.float32)
                return (Z - mean2) / std

            return _xfm

        if spec.get("type") == "minmax":
            self._scaler_kind_ = "minmax"
            st = self._scaler_state_ or {"min": None, "max": None}
            X = np.asarray(X2d, dtype=np.float32)
            mn = X.min(axis=0) if st["min"] is None else np.minimum(st["min"], X.min(axis=0))
            mx = X.max(axis=0) if st["max"] is None else np.maximum(st["max"], X.max(axis=0))
            self._scaler_state_ = {"min": mn, "max": mx}

            def _xfm(Z: np.ndarray) -> np.ndarray:
                st2 = self._scaler_state_
                assert st2 is not None
                mn2 = st2["min"]
                mx2 = st2["max"]
                scale = np.where((mx2 - mn2) > 1e-8, (mx2 - mn2), 1.0)
                return (Z - mn2) / scale

            return _xfm

        # Custom object
        obj = spec.get("obj")
        self._scaler_kind_ = "custom"
        if not hasattr(self, "_scaler_fitted_") or not getattr(self, "_scaler_fitted_", False):
            # Fit once
            try:
                obj.fit(X2d, **(self.scaler_params or {}))
            except TypeError:
                obj.fit(X2d)
            self._scaler_fitted_ = True
        else:
            if hasattr(obj, "partial_fit"):
                obj.partial_fit(X2d)
            else:
                # Fallback: refit on concatenation of small cache if available
                pass

        def _xfm(Z: np.ndarray) -> np.ndarray:
            return obj.transform(Z)

        return _xfm

    def _scaler_inverse_tensor(self, X_ep: torch.Tensor, *, feature_dim: int = -1) -> torch.Tensor:
        """Inverse-transform a torch tensor episode if scaler is active.

        Expects features along last dim by default (B,T,D) or (N,D).
        """
        kind = getattr(self, "_scaler_kind_", None)
        st = getattr(self, "_scaler_state_", None)
        if kind is None:
            return X_ep
        if kind == "standard" and st is not None:
            mean = torch.as_tensor(st["mean"], device=X_ep.device, dtype=X_ep.dtype)
            var = torch.as_tensor(st["M2"] / max(st["n"], 1), device=X_ep.device, dtype=X_ep.dtype)
            std = torch.sqrt(torch.clamp(var, min=1e-8))
            return X_ep * std + mean
        if kind == "minmax" and st is not None:
            mn = torch.as_tensor(st["min"], device=X_ep.device, dtype=X_ep.dtype)
            mx = torch.as_tensor(st["max"], device=X_ep.device, dtype=X_ep.dtype)
            scale = torch.where((mx - mn) > 1e-8, (mx - mn), torch.ones_like(mx))
            return X_ep * scale + mn
        if kind == "custom" and hasattr(self.scaler, "inverse_transform"):
            # Fallback via CPU numpy; small overhead acceptable for context extraction
            X_np = X_ep.detach().cpu().numpy()
            X_inv = self.scaler.inverse_transform(X_np)
            return torch.as_tensor(X_inv, device=X_ep.device, dtype=X_ep.dtype)
        return X_ep

    # Internal helpers
    def _device(self) -> torch.device:
        return choose_device(self.device)

    def _infer_input_shape(self, X: np.ndarray) -> tuple:
        if X.ndim < 2:
            raise ValueError("X must be at least 2D (batch, features...)")
        return tuple(X.shape[1:])

    def _flatten(self, X: np.ndarray) -> np.ndarray:
        return X.reshape(X.shape[0], -1).astype(np.float32, copy=False)

    def _make_optimizer(self, model: torch.nn.Module, lr: Optional[float] = None):
        lr = float(self.lr if lr is None else lr)
        if self.optimizer.lower() == "adamw":
            return torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=self.weight_decay)
        if self.optimizer.lower() == "sgd":
            return torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
        return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=self.weight_decay)

    def _make_loss(self):
        # Built-in strings
        if isinstance(self.loss, str):
            name = self.loss.lower()
            params = self.loss_params or {}
            reduction = self.loss_reduction
            if name in ("l1", "mae"):
                return torch.nn.L1Loss(reduction=reduction)
            if name in ("mse", "l2"):
                return torch.nn.MSELoss(reduction=reduction)
            if name in ("smooth_l1", "huber_smooth"):
                beta = float(params.get("beta", 1.0))
                return torch.nn.SmoothL1Loss(beta=beta, reduction=reduction)
            if name in ("huber",):
                delta = float(params.get("delta", 1.0))
                return torch.nn.HuberLoss(delta=delta, reduction=reduction)
            raise ValueError(f"Unknown loss '{self.loss}'. Supported: mse, l1/mae, smooth_l1, huber, or a callable.")

        # Callable custom loss; may return tensor (any shape) or float
        if callable(self.loss):
            user_fn = self.loss
            params = self.loss_params or {}
            reduction = self.loss_reduction

            def _loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
                out = user_fn(pred, target, **params) if params else user_fn(pred, target)
                if not isinstance(out, torch.Tensor):
                    out = torch.as_tensor(out, dtype=pred.dtype, device=pred.device)
                if out.ndim == 0:
                    return out
                if reduction == "mean":
                    return out.mean()
                if reduction == "sum":
                    return out.sum()
                if reduction == "none":
                    return out
                raise ValueError(f"Unsupported reduction '{reduction}' for custom loss")

            return _loss

        raise TypeError("loss must be a string or a callable returning a scalar tensor")

    # Estimator API
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray | None,
        *,
        validation_data: Optional[tuple[np.ndarray, np.ndarray]] = None,
        verbose: int = 0,
        noisy: Optional[float | np.ndarray] = None,
        hisso: bool = False,
        hisso_window: Optional[int] = None,
        hisso_reward_fn: Optional[Callable[[torch.Tensor, torch.Tensor], torch.Tensor]] = None,
        hisso_context_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        hisso_trans_cost: Optional[float] = None,
    ):
        """Fit the estimator.

        Parameters
        - X: np.ndarray
            Training inputs. Shapes:
              - MLP/flattened: (N, F1, ..., Fk) flattened internally to (N, prod(F*))
              - preserve_shape=True: (N, C, ...) or (N, ..., C) depending on data_format
        - y: np.ndarray
            Targets. Shapes:
              - vector/pooled head: (N, T) or (N,) where T=prod(output_shape) if provided
              - per_element=True: (N, C_out, ...) or (N, ..., C_out) matching X spatial dims
        - validation_data: optional (X_val, y_val) for early stopping/logging
        - verbose: 0/1 to control epoch logging
        - noisy: optional Gaussian input noise std; scalar, per-feature vector, or tensor matching input shape
        - hisso: if True, train via Horizon-Informed Sampling Strategy Optimization (episodic reward)
        - hisso_window: episode/window length for HISSO (default 64)
        """
        seed_all(self.random_state)

        X = np.asarray(X, dtype=np.float32)
        if y is not None:
            y = np.asarray(y, dtype=np.float32)
        if not hisso and y is None:
            raise ValueError("y must be provided when hisso=False")
        # Handle input shape
        self.input_shape_ = self._infer_input_shape(X)

        # Fit/Update scaler on training data and transform X for model input
        X_for_scaler = X
        # Flatten to (N,D) for scaler in non-preserve shape; else treat channel-wise after moveaxis
        if not self.preserve_shape:
            X2d = self._flatten(X_for_scaler)
            xfm = self._scaler_fit_update(X2d)
            if xfm is not None:
                X2d_scaled = xfm(X2d)
                X_scaled = X2d_scaled.reshape(X.shape[0], *self.input_shape_)
            else:
                X_scaled = X
        else:
            # channels-first internal layout
            X_cf = np.moveaxis(X, -1, 1) if self.data_format == "channels_last" else X
            N, C = X_cf.shape[0], int(X_cf.shape[1])
            X2d = X_cf.reshape(N, C, -1).transpose(0, 2, 1).reshape(-1, C)  # (N*spatial, C)
            xfm = self._scaler_fit_update(X2d)
            if xfm is not None:
                X2d_scaled = xfm(X2d)
                X_cf_scaled = X2d_scaled.reshape(N, -1, C).transpose(0, 2, 1).reshape(X_cf.shape)
                X_scaled = np.moveaxis(X_cf_scaled, 1, -1) if self.data_format == "channels_last" else X_cf_scaled
            else:
                X_scaled = X
        X = X_scaled

        # Warn if stateful requested without a state configuration
        if self.stateful and not self.state:
            warnings.warn(
                "stateful=True but no state config provided; stateful mechanics will be disabled. "
                "Pass state={init,rho,beta,max_abs,detach} to enable persistent state.",
                RuntimeWarning,
            )

        # HISSO episodic training branch (Predictive-Extras)
        if hisso:
            if self.preserve_shape:
                raise ValueError("hisso=True currently supports flattened vector inputs only (preserve_shape=False)")
            # Determine primary/extras dims
            primary_dim = int(np.prod(self.input_shape_))
            extras_dim = max(0, int(self.extras))
            out_dim = primary_dim + extras_dim

            # Flatten input for episode sampling
            X_flat = self._flatten(X)
            X_train_arr = X_flat
            lsm_model = None

            # Optional LSM: accept dict config or prebuilt
            if self.lsm is not None:
                try:
                    from .lsm import LSMExpander
                except Exception:
                    LSMExpander = None  # type: ignore
                if isinstance(self.lsm, dict):
                    if LSMExpander is None:
                        raise RuntimeError("LSM components not available")
                    lsm_cfg = dict(self.lsm)
                    od = int(lsm_cfg.pop("output_dim", lsm_cfg.pop("out_channels", 128)))
                    expander = LSMExpander(output_dim=od, **lsm_cfg)
                    expander.fit(X_train_arr, epochs=(self.lsm_pretrain_epochs or 0))
                    lsm_model = expander.model
                    self.lsm = expander
                elif LSMExpander is not None and isinstance(self.lsm, LSMExpander):
                    if (self.lsm.model is None) or (self.lsm_pretrain_epochs and self.lsm_pretrain_epochs > 0):
                        self.lsm.fit(X_train_arr, epochs=(self.lsm_pretrain_epochs or 0))
                    lsm_model = self.lsm.model
                    if lsm_model is None:
                        raise RuntimeError("Provided LSMExpander has no underlying model; call fit() or set .model.")
                elif hasattr(self.lsm, 'forward') and hasattr(self.lsm, 'output_dim'):
                    lsm_model = self.lsm
                else:
                    raise ValueError("lsm must be a dict, an LSMExpander, or a torch.nn.Module with 'output_dim'")

            # Build core PSANN input dim (LSM(base) + extras passthrough)
            if lsm_model is not None:
                base_out = int(getattr(lsm_model, 'output_dim'))
                core_in = base_out + extras_dim
            else:
                core_in = primary_dim + extras_dim

            # Build model unless warm-starting with existing compatible model
            rebuild = True
            if self.warm_start and hasattr(self, "model_") and isinstance(self.model_, nn.Module):
                rebuild = False
            if rebuild:
                core_model = PSANNNet(
                    core_in,
                    out_dim,
                    hidden_layers=self.hidden_layers,
                    hidden_width=self.hidden_width,
                    act_kw=self.activation,
                    state_cfg=(self.state if self.stateful else None),
                    activation_type=self.activation_type,
                    w0=self.w0,
                )
                preproc = None
                if lsm_model is not None:
                    class _BasePlusExtras(torch.nn.Module):
                        def __init__(self, base: torch.nn.Module, base_dim: int, extras_dim: int):
                            super().__init__()
                            self.base = base
                            self.base_dim = int(base_dim)
                            self.extras_dim = int(extras_dim)
                        def forward(self, x: torch.Tensor) -> torch.Tensor:
                            if self.extras_dim <= 0:
                                return self.base(x)
                            xb = x[..., : self.base_dim]
                            xe = x[..., self.base_dim : self.base_dim + self.extras_dim]
                            zb = self.base(xb)
                            return torch.cat([zb, xe], dim=-1)

                    preproc = _BasePlusExtras(lsm_model, base_dim=primary_dim, extras_dim=extras_dim)
                self.model_ = WithPreprocessor(preproc, core_model)
            device = self._device()
            self.model_.to(device)

            # Episodic training with predictive extras
            try:
                from .augmented import PredictiveExtrasConfig, PredictiveExtrasTrainer
                from .episodes import portfolio_log_return_reward
            except Exception as e:
                raise RuntimeError("Predictive extras components not available") from e
            cfg = PredictiveExtrasConfig(
                episode_length=int(hisso_window if hisso_window is not None else 64),
                batch_episodes=32,
                primary_dim=primary_dim,
                extras_dim=extras_dim,
                primary_transform="softmax",
                extras_transform="tanh",
                trans_cost=float(hisso_trans_cost) if hisso_trans_cost is not None else 0.0,
                random_state=self.random_state,
            )
            # If inputs were scaled and user didn't supply a context_extractor, default to inverse-transform for reward context
            default_ctx = (lambda X_ep: X_ep)
            if hisso_context_extractor is None and getattr(self, "_scaler_kind_", None) is not None:
                def _ctx_inv(X_ep: torch.Tensor) -> torch.Tensor:
                    return self._scaler_inverse_tensor(X_ep)
                default_ctx = _ctx_inv

            trainer = PredictiveExtrasTrainer(
                self.model_,
                reward_fn=(
                    hisso_reward_fn if hisso_reward_fn is not None else
                    (lambda alloc, ctx: portfolio_log_return_reward(alloc, ctx, trans_cost=cfg.trans_cost))
                ),
                cfg=cfg,
                device=device,
                lr=float(self.lr),
                input_noise_std=(float(noisy) if noisy is not None else None),
                context_extractor=hisso_context_extractor if hisso_context_extractor is not None else default_ctx,
            )
            trainer.train(X_train_arr, epochs=int(self.epochs), verbose=int(verbose))
            self._hisso_cfg_ = cfg
            self._hisso_trained_ = True
            self.history_ = getattr(trainer, "history", [])
            return self

        if self.preserve_shape:
            if X.ndim < 3:
                raise ValueError("preserve_shape=True requires X with at least 3 dims (N, C, ...).")
            if self.data_format not in {"channels_first", "channels_last"}:
                raise ValueError("data_format must be 'channels_first' or 'channels_last'")
            X_cf = np.moveaxis(X, -1, 1) if self.data_format == "channels_last" else X
            self._internal_input_shape_cf_ = tuple(X_cf.shape[1:])
            in_channels = int(X_cf.shape[1])
            nd = X_cf.ndim - 2
            # Targets
            if self.per_element:
                # Determine desired output channels
                if self.output_shape is not None:
                    n_targets = int(self.output_shape[-1] if self.data_format == "channels_last" else self.output_shape[0])
                else:
                    # Infer from targets
                    if self.data_format == "channels_last":
                        if y.ndim == X.ndim:
                            n_targets = int(y.shape[-1])
                        elif y.ndim == X.ndim - 1:
                            n_targets = 1
                        else:
                            raise ValueError("y must match X spatial dims, with optional channel last.")
                    else:
                        if y.ndim == X_cf.ndim:
                            n_targets = int(y.shape[1])
                        elif y.ndim == X_cf.ndim - 1:
                            n_targets = 1
                        else:
                            raise ValueError("y must match X spatial dims, with optional channel first.")
                # Prepare y in channels-first layout
                if self.data_format == "channels_last":
                    if y.ndim == X.ndim:
                        y_cf = np.moveaxis(y, -1, 1)
                    elif y.ndim == X.ndim - 1:
                        if n_targets != 1:
                            raise ValueError(f"Provided output_shape implies {n_targets} channels but y has no channel dimension")
                        y_cf = y[:, None, ...]
                else:
                    if y.ndim == X_cf.ndim:
                        y_cf = y
                    elif y.ndim == X_cf.ndim - 1:
                        if n_targets != 1:
                            raise ValueError(f"Provided output_shape implies {n_targets} channels but y has no channel dimension")
                        y_cf = y[:, None, ...]
            else:
                # pooled/vector targets
                y_vec = y.reshape(y.shape[0], -1) if y.ndim > 2 else (y[:, None] if y.ndim == 1 else y)
                if self.output_shape is not None:
                    n_targets = int(np.prod(self.output_shape))
                    if y_vec.shape[1] != n_targets:
                        raise ValueError(f"y has {y_vec.shape[1]} targets, expected {n_targets} from output_shape")
                else:
                    n_targets = int(y_vec.shape[1])
                y_cf = y_vec

            # Optional Conv LSM integration
            lsm_model = None
            if self.lsm is not None:
                try:
                    from .lsm import LSMConv2dExpander, LSMConv2d
                except Exception:
                    LSMConv2dExpander = None  # type: ignore
                    LSMConv2d = None  # type: ignore
                if nd == 2:
                    if isinstance(self.lsm, dict):
                        if LSMConv2dExpander is None:
                            raise RuntimeError("LSM components not available")
                        lsm_cfg = dict(self.lsm)
                        oc = int(lsm_cfg.pop("out_channels", lsm_cfg.pop("output_dim", 128)))
                        expander = LSMConv2dExpander(out_channels=oc, **lsm_cfg)
                        expander.fit(X_cf, epochs=(self.lsm_pretrain_epochs or 0))
                        lsm_model = expander.model
                        self.lsm = expander
                        in_channels = int(getattr(expander, 'out_channels', oc))
                    elif LSMConv2dExpander is not None and isinstance(self.lsm, LSMConv2dExpander):
                        # Ensure underlying model exists (allow 0-epoch init)
                        if (self.lsm.model is None) or (self.lsm_pretrain_epochs and self.lsm_pretrain_epochs > 0):
                            self.lsm.fit(X_cf, epochs=(self.lsm_pretrain_epochs or 0))
                        lsm_model = self.lsm.model
                        if lsm_model is None:
                            raise RuntimeError("Provided LSMConv2dExpander has no underlying model; call fit() or set .model.")
                        in_channels = int(self.lsm.out_channels)
                    elif LSMConv2d is not None and isinstance(self.lsm, LSMConv2d):
                        lsm_model = self.lsm
                        in_channels = int(getattr(lsm_model, 'out_channels'))
                    elif hasattr(self.lsm, 'forward') and hasattr(self.lsm, 'out_channels'):
                        lsm_model = self.lsm
                        in_channels = int(getattr(lsm_model, 'out_channels'))
                else:
                    if self.lsm is not None:
                        raise ValueError("Conv LSM is currently supported for 2D inputs only.")

            # Model (rebuild unless warm-starting with existing compatible model)
            rebuild = True
            if self.warm_start and hasattr(self, "model_") and isinstance(self.model_, nn.Module):
                rebuild = False
            if not rebuild:
                # assume existing model_ matches architecture
                pass
            elif nd == 1:
                self.model_ = PSANNConv1dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    activation_type=self.activation_type,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            elif nd == 2:
                self.model_ = PSANNConv2dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    activation_type=self.activation_type,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            elif nd == 3:
                self.model_ = PSANNConv3dNet(
                    in_channels,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_channels=self.hidden_width,
                    kernel_size=self.conv_kernel_size,
                    act_kw=self.activation,
                    activation_type=self.activation_type,
                    w0=self.w0,
                    segmentation_head=self.per_element,
                )
            else:
                raise ValueError(f"Unsupported number of spatial dims: {nd}. Supported: 1, 2, 3.")
            # Compose full model with optional preprocessor
            if rebuild:
                core_model = self.model_
                if lsm_model is not None:
                    # Freeze or train preproc according to lsm_train
                    if not self.lsm_train:
                        for p in lsm_model.parameters():
                            p.requires_grad = False
                    self.model_ = WithPreprocessor(lsm_model, core_model)
                else:
                    self.model_ = WithPreprocessor(None, core_model)
            X_train_arr = X_cf.astype(np.float32, copy=False)
        else:
            n_features = int(np.prod(self.input_shape_))
            X_flat = self._flatten(X)
            y_vec = y.reshape(y.shape[0], -1) if y.ndim > 1 else y[:, None]
            if self.output_shape is not None:
                n_targets = int(np.prod(self.output_shape))
                if y_vec.shape[1] != n_targets:
                    raise ValueError(f"y has {y_vec.shape[1]} targets, expected {n_targets} from output_shape")
            else:
                n_targets = int(y_vec.shape[1])

            # Optional LSM integration (flattened path only)
            X_train_arr = X_flat
            lsm_model = None
        if self.lsm is not None:
            try:
                from .lsm import LSMExpander
            except Exception:
                LSMExpander = None  # type: ignore
            if isinstance(self.lsm, dict):
                if LSMExpander is None:
                    raise RuntimeError("LSM components not available")
                lsm_cfg = dict(self.lsm)
                od = int(lsm_cfg.pop("output_dim", lsm_cfg.pop("out_channels", 128)))
                expander = LSMExpander(output_dim=od, **lsm_cfg)
                expander.fit(X_train_arr, epochs=(self.lsm_pretrain_epochs or 0))
                lsm_model = expander.model
                self.lsm = expander
                lsm_out = int(od)
            elif LSMExpander is not None and isinstance(self.lsm, LSMExpander):
                if (self.lsm.model is None) or (self.lsm_pretrain_epochs and self.lsm_pretrain_epochs > 0):
                    # Initialize underlying model (0 epochs allowed)
                    self.lsm.fit(X_train_arr, epochs=(self.lsm_pretrain_epochs or 0))
                lsm_model = self.lsm.model
                if lsm_model is None:
                    raise RuntimeError("Provided LSMExpander has no underlying model; call fit() or set .model.")
                lsm_out = int(self.lsm.output_dim)
            elif hasattr(self.lsm, 'forward'):
                lsm_model = self.lsm
                if not hasattr(lsm_model, 'output_dim'):
                    raise ValueError("Custom LSM module must define attribute 'output_dim'")
                lsm_out = int(getattr(lsm_model, 'output_dim'))
            else:
                raise ValueError("lsm must be an LSMExpander or a torch.nn.Module with 'output_dim'")

            # Build PSANN over (possibly expanded) features
            if self.lsm is not None and not self.preserve_shape:
                if lsm_model is not None and hasattr(lsm_model, 'output_dim'):
                    in_dim_psann = int(getattr(lsm_model, 'output_dim'))
                elif hasattr(self.lsm, 'output_dim'):
                    in_dim_psann = int(getattr(self.lsm, 'output_dim'))
                else:
                    in_dim_psann = int(X_train_arr.shape[1]) if isinstance(X_train_arr, np.ndarray) else int(n_features)
            else:
                in_dim_psann = int(X_train_arr.shape[1]) if isinstance(X_train_arr, np.ndarray) else int(n_features)
            # Rebuild unless warm-starting with existing model
            rebuild = True
            if self.warm_start and hasattr(self, "model_") and isinstance(self.model_, nn.Module):
                rebuild = False
            if rebuild:
                core_model = PSANNNet(
                    in_dim_psann,
                    n_targets,
                    hidden_layers=self.hidden_layers,
                    hidden_width=self.hidden_width,
                    act_kw=self.activation,
                    state_cfg=(self.state if self.stateful else None),
                    activation_type=self.activation_type,
                    w0=self.w0,
                )
                y_cf = y_vec
                if lsm_model is not None:
                    if not self.lsm_train:
                        for p in lsm_model.parameters():
                            p.requires_grad = False
                    self.model_ = WithPreprocessor(lsm_model, core_model)
                else:
                    self.model_ = WithPreprocessor(None, core_model)
        device = self._device()
        self.model_.to(device)

        # Optimizer: include preproc params if training; else only core (requires_grad governs)
        if self.lsm_train and lsm_model is not None:
            # Two param groups to allow separate LR
            params = [
                {"params": self.model_.core.parameters(), "lr": self.lr},
                {"params": self.model_.preproc.parameters(), "lr": float(self.lsm_lr) if self.lsm_lr is not None else self.lr},
            ]
            if self.optimizer.lower() == "adamw":
                opt = torch.optim.AdamW(params, weight_decay=self.weight_decay)
            elif self.optimizer.lower() == "sgd":
                opt = torch.optim.SGD(params, momentum=0.9)
            else:
                opt = torch.optim.Adam(params, weight_decay=self.weight_decay)
        else:
            opt = self._make_optimizer(self.model_)
        loss_fn = self._make_loss()

        # Always feed original inputs to the model (wrapper handles preprocessing)
        ds = TensorDataset(torch.from_numpy(X_train_arr), torch.from_numpy(y_cf.astype(np.float32, copy=False)))
        # If state should persist across batches/epoch, disable shuffling to preserve temporal order
        shuffle_batches = True
        if self.stateful and self.state_reset in ("epoch", "none"):
            shuffle_batches = False
        dl = DataLoader(ds, batch_size=self.batch_size, shuffle=shuffle_batches, num_workers=self.num_workers)

        # Prepare validation tensors if provided
        X_val_t = y_val_t = None
        if validation_data is not None:
            Xv, yv = validation_data
            Xv = np.asarray(Xv, dtype=np.float32)
            yv = np.asarray(yv, dtype=np.float32)
            if self.preserve_shape:
                Xv_cf = np.moveaxis(Xv, -1, 1) if self.data_format == "channels_last" else Xv
                if Xv_cf.shape[1] != self._internal_input_shape_cf_[0]:
                    raise ValueError("validation_data channels mismatch.")
                X_val_t = torch.from_numpy(Xv_cf).to(device)
                if self.per_element:
                    if self.data_format == "channels_last":
                        if yv.ndim == Xv.ndim:
                            yv_cf = np.moveaxis(yv, -1, 1)
                        elif yv.ndim == Xv.ndim - 1:
                            yv_cf = yv[:, None, ...]
                        else:
                            raise ValueError("validation y must match X spatial dims, optional channel last.")
                    else:
                        if yv.ndim == Xv_cf.ndim:
                            yv_cf = yv
                        elif yv.ndim == Xv_cf.ndim - 1:
                            yv_cf = yv[:, None, ...]
                        else:
                            raise ValueError("validation y must match X spatial dims, optional channel first.")
                    y_val_t = torch.from_numpy(yv_cf.astype(np.float32, copy=False)).to(device)
                else:
                    y_val_t = torch.from_numpy(yv.reshape(yv.shape[0], -1).astype(np.float32, copy=False)).to(device)
            else:
                n_features = int(np.prod(self.input_shape_))
                if tuple(Xv.shape[1:]) != self.input_shape_:
                    if int(np.prod(Xv.shape[1:])) != n_features:
                        raise ValueError(
                            f"validation_data X has shape {Xv.shape[1:]}, expected {self.input_shape_} (prod must match {n_features})."
                        )
                X_val_t = torch.from_numpy(self._flatten(Xv)).to(device)
                y_val_t = torch.from_numpy(yv.reshape(yv.shape[0], -1).astype(np.float32, copy=False)).to(device)

        # Prepare per-feature noise std (broadcast over batch) if requested
        noise_std_t: Optional[torch.Tensor] = None
        if noisy is not None:
            if self.preserve_shape:
                internal_shape = self._internal_input_shape_cf_
                if np.isscalar(noisy):
                    std = np.full((1, *internal_shape), float(noisy), dtype=np.float32)
                else:
                    arr = np.asarray(noisy, dtype=np.float32)
                    if tuple(arr.shape) == internal_shape:
                        std = arr.reshape(1, *internal_shape)
                    elif tuple(arr.shape) == self.input_shape_ and self.data_format == "channels_last":
                        std = np.moveaxis(arr, -1, 0).reshape(1, *internal_shape)
                    elif arr.ndim == 1 and arr.size == int(np.prod(internal_shape)):
                        std = arr.reshape(1, *internal_shape)
                    else:
                        raise ValueError(
                            f"noisy shape {arr.shape} not compatible with input shape {self.input_shape_}"
                        )
                noise_std_t = torch.from_numpy(std).to(device)
            else:
                n_features = int(np.prod(self.input_shape_))
                if np.isscalar(noisy):
                    std = np.full((1, n_features), float(noisy), dtype=np.float32)
                else:
                    arr = np.asarray(noisy, dtype=np.float32)
                    if arr.ndim == 1 and arr.shape[0] == n_features:
                        std = arr.reshape(1, -1)
                    elif tuple(arr.shape) == self.input_shape_:
                        std = arr.reshape(1, -1)
                    else:
                        raise ValueError(
                            f"noisy shape {arr.shape} not compatible with input shape {self.input_shape_} or flattened size {n_features}"
                        )
                noise_std_t = torch.from_numpy(std).to(device)

        best = float("inf")
        patience = self.patience
        best_state: Optional[Dict[str, torch.Tensor]] = None

        for epoch in range(self.epochs):
            if self.stateful and self.state_reset == "epoch" and hasattr(self.model_, "reset_state"):
                try:
                    self.model_.reset_state()
                except Exception:
                    pass
            self.model_.train()
            total = 0.0
            count = 0
            for xb, yb in dl:
                if self.stateful and self.state_reset == "batch" and hasattr(self.model_, "reset_state"):
                    # Reset at each batch to prevent leakage between batches
                    try:
                        self.model_.reset_state()
                    except Exception:
                        pass
                xb, yb = xb.to(device), yb.to(device)
                if noise_std_t is not None:
                    # Sample Gaussian noise per feature; broadcast over batch
                    noise = torch.randn_like(xb) * noise_std_t
                    xb = xb + noise
                opt.zero_grad()
                # If using LSM joint training, transform on the fly
                if self.lsm_train and self.lsm is not None and lsm_model is not None:
                    xb_in = lsm_model(xb)
                else:
                    xb_in = xb
                pred = self.model_(xb_in)
                loss = loss_fn(pred, yb)
                loss.backward()
                opt.step()
                if hasattr(self.model_, "commit_state_updates"):
                    self.model_.commit_state_updates()
                bs = xb.shape[0]
                total += float(loss.item()) * bs
                count += bs
            epoch_loss = total / max(count, 1)

            # Validation loss (if provided)
            val_loss = None
            if X_val_t is not None and y_val_t is not None:
                self.model_.eval()
                with torch.no_grad():
                    if self.lsm is not None and not self.preserve_shape:
                        if self.lsm_train and lsm_model is not None:
                            X_val_in = lsm_model(X_val_t)
                        else:
                            # Offline transform for validation
                            if hasattr(self.lsm, 'transform'):
                                X_val_in = torch.from_numpy(self.lsm.transform(X_val_t.cpu().numpy())).to(device)
                            elif hasattr(self.lsm, 'forward'):
                                X_val_in = self.lsm(X_val_t)
                            else:
                                X_val_in = X_val_t
                    else:
                        X_val_in = X_val_t
                    pred_val = self.model_(X_val_in)
                    val_loss = float(loss_fn(pred_val, y_val_t).item())

            # Logging
            if verbose:
                if val_loss is not None:
                    print(f"Epoch {epoch+1}/{self.epochs} - loss: {epoch_loss:.6f} - val_loss: {val_loss:.6f}")
                else:
                    print(f"Epoch {epoch+1}/{self.epochs} - loss: {epoch_loss:.6f}")

            # Early stopping: prefer validation loss when available
            metric = val_loss if val_loss is not None else epoch_loss
            if self.early_stopping:
                if metric + 1e-12 < best:
                    best = metric
                    patience = self.patience
                    best_state = {k: v.detach().cpu().clone() for k, v in self.model_.state_dict().items()}
                else:
                    patience -= 1
                    if patience <= 0 and best_state is not None:
                        if verbose:
                            print(f"Early stopping at epoch {epoch+1} (best metric: {best:.6f})")
                        self.model_.load_state_dict(best_state)
                        break
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict outputs for X.

        Returns
        - MLP/pooled head: (N, T) if T>1, else 1D shape (N,)
        - per_element=True: channels-first if data_format='channels_first',
          or channels-last if 'channels_last'. Spatial dims mirror input.
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        X = np.asarray(X, dtype=np.float32)
        if not hasattr(self, "input_shape_"):
            # Fallback to observed shape
            self.input_shape_ = tuple(X.shape[1:])
        # Validate and prepare
        if self.preserve_shape:
            X_arr = np.moveaxis(X, -1, 1) if self.data_format == "channels_last" else X
            if X_arr.shape[1] != self._internal_input_shape_cf_[0]:
                raise ValueError("X channels mismatch for predict().")
        else:
            if tuple(X.shape[1:]) != self.input_shape_:
                if int(np.prod(X.shape[1:])) != int(np.prod(self.input_shape_)):
                    raise ValueError(
                        f"X has shape {X.shape[1:]}, expected {self.input_shape_} (prod must match)."
                    )
            X_arr = self._flatten(X)
        # Apply scaler if active
        if getattr(self, "_scaler_kind_", None) is not None:
            if not self.preserve_shape:
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    X_arr = (X_arr - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    X_arr = (X_arr - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    X_arr = self.scaler.transform(X_arr)
            else:
                # Scale per-channel in channels-first layout
                N, C = X_arr.shape[0], int(X_arr.shape[1])
                X2d = X_arr.reshape(N, C, -1).transpose(0, 2, 1).reshape(-1, C)
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    X2d = (X2d - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    X2d = (X2d - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    X2d = self.scaler.transform(X2d)
                X_arr = X2d.reshape(N, -1, C).transpose(0, 2, 1).reshape(X_arr.shape)
        device = self._device()
        self.model_.eval()
        with torch.no_grad():
            # Apply scaler if active (non-preserve shape path); preserve_shape handled before model input formatting
            Xin = torch.from_numpy(X_arr).to(device)
            out = self.model_(Xin).cpu().numpy()
        if self.preserve_shape and self.per_element:
            # Return in input's data_format
            if self.data_format == "channels_last":
                out = np.moveaxis(out, 1, -1)
            return out
        else:
            if out.shape[1] == 1:
                out = out[:, 0]
            return out

    # Stateful inference helpers
    def reset_state(self) -> None:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if hasattr(self.model_, "reset_state"):
            self.model_.reset_state()

    def step(self, x_t: np.ndarray, y_t: Optional[np.ndarray] = None, update: bool = False) -> np.ndarray | float:
        """Single-step inference; optionally apply an immediate parameter update.

        Returns a scalar (float) for single-target models or a 1D array for multi-target.
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("step() requires stateful=True on the estimator.")
        # Prepare single input respecting preserve_shape/flatten
        xt = np.asarray(x_t, dtype=np.float32)
        if xt.ndim == 1:
            xt = xt[None, :]
        if self.preserve_shape:
            xt = np.moveaxis(xt, -1, 1) if self.data_format == "channels_last" else xt
        else:
            xt = xt.reshape(xt.shape[0], -1)
        # Apply scaler if active
        if getattr(self, "_scaler_kind_", None) is not None:
            if not self.preserve_shape:
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    xt = (xt - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    xt = (xt - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    xt = self.scaler.transform(xt)
            else:
                N, C = xt.shape[0], int(xt.shape[1])
                X2d = xt.reshape(N, C, -1).transpose(0, 2, 1).reshape(-1, C)
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    X2d = (X2d - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    X2d = (X2d - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    X2d = self.scaler.transform(X2d)
                xt = X2d.reshape(N, -1, C).transpose(0, 2, 1)
        device = self._device()
        # Temporarily set to train mode to allow state updates
        prev_mode = self.model_.training
        self.model_.train()
        with torch.no_grad():
            out = self.model_(torch.from_numpy(xt).to(device)).cpu().numpy()
        if hasattr(self.model_, "commit_state_updates"):
            self.model_.commit_state_updates()
        # Optional online update with target, without additional state update
        if update and y_t is not None:
            # Ensure streaming optimizer
            if not hasattr(self, "_stream_opt") or self._stream_opt is None:
                self._stream_opt = self._make_optimizer(self.model_, lr=self.stream_lr)
                self._stream_loss = self._make_loss()
            # Disable state updates during gradient pass
            if hasattr(self.model_, "set_state_updates"):
                self.model_.set_state_updates(False)
            self.model_.train()
            opt = self._stream_opt
            loss_fn = self._stream_loss
            opt.zero_grad()
            xb = torch.from_numpy(xt).to(device)
            pred = self.model_(xb)
            yt = np.asarray(y_t, dtype=np.float32)
            if yt.ndim == 0:
                yt = yt[None]
            if yt.ndim == 1:
                yt = yt[:, None]
            yb = torch.from_numpy(yt).to(device)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            if hasattr(self.model_, "commit_state_updates"):
                self.model_.commit_state_updates()
            if hasattr(self.model_, "set_state_updates"):
                self.model_.set_state_updates(True)
        # Restore mode
        self.model_.train(prev_mode)
        if out.shape[1] == 1:
            return out[0, 0]
        return out[0]

    def predict_sequence(self, X_seq: np.ndarray, *, reset_state: bool = True, return_sequence: bool = False) -> np.ndarray:
        """Free-run over a sequence preserving internal state across steps.

        If return_sequence=False, returns last prediction; else returns the full sequence.
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("predict_sequence() requires stateful=True on the estimator.")
        Xs = np.asarray(X_seq, dtype=np.float32)
        if Xs.ndim == 3:
            if Xs.shape[0] != 1:
                raise ValueError("Only batch size 1 supported for predict_sequence (got N != 1).")
            Xs = Xs[0]
        if Xs.ndim != 2:
            raise ValueError("X_seq must be (T, D) or (1, T, D)")
        if reset_state:
            self.reset_state()
        outs = []
        for t in range(Xs.shape[0]):
            outs.append(self.step(Xs[t]))
        outs = np.asarray(outs)
        return outs if return_sequence else outs[-1]

    def predict_sequence_online(self, X_seq: np.ndarray, y_seq: np.ndarray, *, reset_state: bool = True) -> np.ndarray:
        """Online prediction with per-step target updates.

        - Preserves internal state across steps (no resets mid-sequence).
        - After each prediction, immediately updates model params with the true target.
        - Returns the sequence of predictions.
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not self.stateful:
            raise RuntimeError("predict_sequence_online() requires stateful=True")
        Xs = np.asarray(X_seq, dtype=np.float32)
        ys = np.asarray(y_seq, dtype=np.float32)
        if Xs.ndim == 3:
            if Xs.shape[0] != 1:
                raise ValueError("Only batch size 1 supported (got N != 1)")
            Xs = Xs[0]
        if Xs.ndim != 2:
            raise ValueError("X_seq must be (T, D) or (1, T, D)")
        if ys.ndim == 1:
            ys = ys[:, None]
        if ys.shape[0] != Xs.shape[0]:
            raise ValueError("y_seq must match X_seq length")
        if reset_state:
            self.reset_state()
        outs = []
        for t in range(Xs.shape[0]):
            yhat_t = self.step(Xs[t], y_t=ys[t], update=True)
            outs.append(yhat_t)
        return np.asarray(outs)

    # ------------------------- HISSO convenience methods -------------------------
    @torch.no_grad()
    def hisso_infer_series(self, X_obs: np.ndarray, *, E0: Optional[np.ndarray] = None) -> tuple[np.ndarray, np.ndarray]:
        """If trained with hisso=True, roll out allocations and extras over a series.

        Returns (primary_allocations, extras_seq) with shapes (N, M) and (N+1, K).
        """
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not getattr(self, "_hisso_trained_", False):
            raise RuntimeError("hisso_infer_series() requires fit(..., hisso=True)")
        try:
            from .augmented import PredictiveExtrasTrainer
            from .episodes import portfolio_log_return_reward as _port_rew
        except Exception as e:
            raise RuntimeError("Predictive extras components not available") from e
        cfg = getattr(self, "_hisso_cfg_", None)
        if cfg is None:
            raise RuntimeError("Missing HISSO config on estimator.")
        # Prepare context extractor that inverts scaling if active
        def _ctx(X_ep: torch.Tensor) -> torch.Tensor:
            return self._scaler_inverse_tensor(X_ep)
        tr = PredictiveExtrasTrainer(
            self.model_,
            reward_fn=lambda alloc, ctx: _port_rew(alloc, ctx, trans_cost=cfg.trans_cost),
            cfg=cfg,
            device=self._device(),
            context_extractor=_ctx,
        )
        # Apply scaler to observed inputs for model inference
        X_in = np.asarray(X_obs, dtype=np.float32)
        if getattr(self, "_scaler_kind_", None) is not None:
            if self.preserve_shape:
                # Only vector HISSO supported currently
                pass
            else:
                X2d = X_in.reshape(X_in.shape[0], -1)
                # Reuse transform using current state
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    X2d = (X2d - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    X2d = (X2d - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    X2d = self.scaler.transform(X2d)
                X_in = X2d.reshape(X_in.shape)
        prim, ex = tr.infer_series(X_in, E0=E0)
        return prim, ex

    @torch.no_grad()
    def hisso_evaluate_reward(self, X_obs: np.ndarray, *, n_batches: int = 8) -> float:
        """Evaluate average episode reward after HISSO training."""
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() first.")
        if not getattr(self, "_hisso_trained_", False):
            raise RuntimeError("hisso_evaluate_reward() requires fit(..., hisso=True)")
        try:
            from .augmented import PredictiveExtrasTrainer
            from .episodes import portfolio_log_return_reward as _port_rew
        except Exception as e:
            raise RuntimeError("Predictive extras components not available") from e
        cfg = getattr(self, "_hisso_cfg_", None)
        if cfg is None:
            raise RuntimeError("Missing HISSO config on estimator.")
        def _ctx(X_ep: torch.Tensor) -> torch.Tensor:
            return self._scaler_inverse_tensor(X_ep)
        tr = PredictiveExtrasTrainer(
            self.model_,
            reward_fn=lambda alloc, ctx: _port_rew(alloc, ctx, trans_cost=cfg.trans_cost),
            cfg=cfg,
            device=self._device(),
            context_extractor=_ctx,
        )
        X_in = np.asarray(X_obs, dtype=np.float32)
        if getattr(self, "_scaler_kind_", None) is not None:
            if not self.preserve_shape:
                X2d = X_in.reshape(X_in.shape[0], -1)
                if self._scaler_kind_ == "standard":
                    st = self._scaler_state_
                    mean = st["mean"]; var = st["M2"]/max(st["n"],1); std = np.sqrt(np.maximum(var,1e-8)).astype(np.float32)
                    X2d = (X2d - mean) / std
                elif self._scaler_kind_ == "minmax":
                    st = self._scaler_state_
                    mn = st["min"]; mx = st["max"]; scale = np.where((mx-mn)>1e-8, (mx-mn), 1.0)
                    X2d = (X2d - mn) / scale
                elif self._scaler_kind_ == "custom" and hasattr(self.scaler, "transform"):
                    X2d = self.scaler.transform(X2d)
                X_in = X2d.reshape(X_in.shape)
        return float(tr.evaluate_reward(X_in, n_batches=int(n_batches)))

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        y_pred = self.predict(X)
        try:
            return float(_sk_r2_score(y, y_pred))
        except Exception:
            # Minimal R^2 fallback
            y = np.asarray(y)
            y_pred = np.asarray(y_pred)
            u = ((y - y_pred) ** 2).sum()
            v = ((y - y.mean()) ** 2).sum()
            return float(1.0 - (u / v if v != 0 else np.nan))

    # Persistence
    def save(self, path: str) -> None:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model is not fitted. Call fit() before save().")
        params = self.get_params(deep=False) if hasattr(self, "get_params") else {}
        meta: Dict[str, Any] = {}
        # Avoid trying to pickle a custom callable in params
        if callable(params.get("loss", None)):
            params["loss"] = "mse"
            meta["note"] = "Original loss was a custom callable and is not serialized; defaulted to 'mse'."
        # Record integrated preprocessor (LSM) spec if present
        preproc_meta: Dict[str, Any] | None = None
        if hasattr(self, "model_") and isinstance(self.model_, torch.nn.Module) and hasattr(self.model_, "preproc"):
            pre = getattr(self.model_, "preproc")
            if pre is not None:
                # Unwrap helper wrappers (e.g., base+extras)
                pre0 = getattr(pre, "base", pre)
                preproc_meta = {"present": True, "type": pre0.__class__.__name__}
                # Try to serialize key structural args
                try:
                    if pre0.__class__.__name__ == "LSM":
                        spec = {
                            "input_dim": int(getattr(pre0, "input_dim", 0)),
                            "output_dim": int(getattr(pre0, "output_dim", 0)),
                            "hidden_layers": int(getattr(pre0, "hidden_layers", 0)),
                            "hidden_width": int(getattr(pre0, "hidden_width", 0)),
                            "sparsity": float(getattr(pre0, "sparsity", 0.8)) if hasattr(pre0, "sparsity") else 0.8,
                            "nonlinearity": str(getattr(pre0, "nonlinearity", "sine")) if hasattr(pre0, "nonlinearity") else "sine",
                        }
                        preproc_meta["spec"] = spec
                    elif pre0.__class__.__name__ == "LSMConv2d":
                        # Deduce parameters
                        nonlin = "sine"
                        try:
                            import torch as _t
                            if getattr(pre0, "_act", None) is _t.sin:
                                nonlin = "sine"
                            elif getattr(pre0, "_act", None) is _t.tanh:
                                nonlin = "tanh"
                            else:
                                from torch.nn.functional import relu as _relu
                                if getattr(pre0, "_act", None) is _relu:
                                    nonlin = "relu"
                        except Exception:
                            pass
                        ks = 1
                        try:
                            if len(getattr(pre0, "body", [])) > 0:
                                ks = int(getattr(pre0.body[0], "kernel_size", (1,))[0])
                        except Exception:
                            pass
                        hidden_channels = 128
                        try:
                            if len(getattr(pre0, "body", [])) > 0:
                                hidden_channels = int(pre0.body[0].out_channels)
                        except Exception:
                            pass
                        spec = {
                            "in_channels": int(getattr(pre0, "in_channels", 0)) if hasattr(pre0, "in_channels") else None,
                            "out_channels": int(getattr(pre0, "out_channels", 0)) if hasattr(pre0, "out_channels") else None,
                            "hidden_layers": int(len(getattr(pre0, "body", []))),
                            "hidden_channels": hidden_channels,
                            "kernel_size": ks,
                            "sparsity": float(getattr(pre0, "sparsity", 0.8)) if hasattr(pre0, "sparsity") else 0.8,
                            "nonlinearity": nonlin,
                        }
                        preproc_meta["spec"] = spec
                except Exception:
                    pass
        # Do not pickle the original 'lsm' object in params; state captures integrated weights
        if "lsm" in params:
            params["lsm"] = None
        if preproc_meta is not None:
            meta["preproc_meta"] = preproc_meta
        if hasattr(self, "input_shape_"):
            meta["input_shape"] = tuple(self.input_shape_)
        meta["preserve_shape"] = bool(getattr(self, "preserve_shape", False))
        meta["data_format"] = getattr(self, "data_format", "channels_first")
        if hasattr(self, "_internal_input_shape_cf_"):
            meta["internal_input_shape_cf"] = tuple(self._internal_input_shape_cf_)
        meta["per_element"] = bool(getattr(self, "per_element", False))
        # Serialize scaler state if available (built-in scalers only)
        if getattr(self, "_scaler_kind_", None) in {"standard", "minmax"} and getattr(self, "_scaler_state_", None) is not None:
            meta["scaler"] = {
                "kind": self._scaler_kind_,
                "state": {
                    k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in self._scaler_state_.items()
                },
            }
        elif getattr(self, "_scaler_kind_", None) == "custom":
            meta.setdefault("warnings", []).append("Custom scaler was used but is not serialized; set it manually after load if needed.")
        payload = {
            "class": "PSANNRegressor",
            "params": params,
            "state_dict": self.model_.state_dict(),
            "meta": meta,
        }
        torch.save(payload, path)

    @classmethod
    def load(cls, path: str, map_location: Optional[str | torch.device] = None) -> "PSANNRegressor":
        payload = torch.load(path, map_location=map_location or "cpu")
        params = payload.get("params", {})
        obj = cls(**params)
        state = payload["state_dict"]
        meta = payload.get("meta", {})
        # Check for integrated preprocessor
        preproc = None
        pre_meta = meta.get("preproc_meta", None)
        if pre_meta and pre_meta.get("present"):
            ptype = pre_meta.get("type")
            spec = pre_meta.get("spec", {})
            try:
                if ptype == "LSM":
                    from .lsm import LSM  # type: ignore
                    preproc = LSM(
                        input_dim=int(spec.get("input_dim", 0)),
                        output_dim=int(spec.get("output_dim", 0)),
                        hidden_layers=int(spec.get("hidden_layers", 2)),
                        hidden_width=int(spec.get("hidden_width", 128)),
                        sparsity=float(spec.get("sparsity", 0.8)),
                        nonlinearity=str(spec.get("nonlinearity", "sine")),
                    )
                elif ptype == "LSMConv2d":
                    from .lsm import LSMConv2d  # type: ignore
                    preproc = LSMConv2d(
                        in_channels=int(spec.get("in_channels", 0)),
                        out_channels=int(spec.get("out_channels", 0)),
                        hidden_layers=int(spec.get("hidden_layers", 1)),
                        hidden_channels=int(spec.get("hidden_channels", 128)),
                        kernel_size=int(spec.get("kernel_size", 1)),
                        sparsity=float(spec.get("sparsity", 0.8)),
                        nonlinearity=str(spec.get("nonlinearity", "sine")),
                    )
            except Exception:
                preproc = None

        # Determine core architecture from namespaced keys
        # Prefer MLP if 'core.body.0.linear.weight' exists; else check conv
        out_dim = None
        if "core.head.weight" in state:
            out_dim = state["core.head.weight"].shape[0]
        if out_dim is None and "core.fc.weight" in state:
            out_dim = state["core.fc.weight"].shape[0]
        if "core.body.0.linear.weight" in state:
            in_dim = state["core.body.0.linear.weight"].shape[1] if obj.hidden_layers > 0 else state["core.head.weight"].shape[1]
            core = PSANNNet(
                int(in_dim),
                int(out_dim),
                hidden_layers=obj.hidden_layers,
                hidden_width=obj.hidden_width,
                act_kw=obj.activation,
                state_cfg=(obj.state if getattr(obj, "stateful", False) else None),
                w0=obj.w0,
            )
        else:
            # Convolutional
            if "core.body.0.conv.weight" not in state:
                raise RuntimeError("Unrecognized state dict: cannot determine MLP or Conv architecture.")
            w = state["core.body.0.conv.weight"]
            in_channels = int(w.shape[1])
            nd = w.ndim - 2
            seg = "core.head.weight" in state and state["core.head.weight"].ndim >= 3 and "core.fc.weight" not in state
            if nd == 1:
                core = PSANNConv1dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            elif nd == 2:
                core = PSANNConv2dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            elif nd == 3:
                core = PSANNConv3dNet(
                    in_channels,
                    int(out_dim),
                    hidden_layers=obj.hidden_layers,
                    hidden_channels=obj.hidden_width,
                    kernel_size=getattr(obj, "conv_kernel_size", 1),
                    act_kw=obj.activation,
                    w0=obj.w0,
                    segmentation_head=seg,
                )
            else:
                raise RuntimeError("Unsupported convolutional kernel dimensionality in saved state.")
        obj.model_ = WithPreprocessor(preproc, core)
        obj.model_.load_state_dict(state)
        obj.model_.to(choose_device(obj.device))
        # Restore input shape if available
        if "input_shape" in meta:
            obj.input_shape_ = tuple(meta["input_shape"])  # type: ignore[assignment]
        if "preserve_shape" in meta:
            obj.preserve_shape = bool(meta["preserve_shape"])  # type: ignore[assignment]
        if "data_format" in meta:
            obj.data_format = str(meta["data_format"])  # type: ignore[assignment]
        if "internal_input_shape_cf" in meta:
            obj._internal_input_shape_cf_ = tuple(meta["internal_input_shape_cf"])  # type: ignore[assignment]
        if "per_element" in meta:
            obj.per_element = bool(meta["per_element"])  # type: ignore[assignment]
        # Restore scaler state if present
        sc = meta.get("scaler")
        if isinstance(sc, dict) and sc.get("kind") in {"standard", "minmax"}:
            obj._scaler_kind_ = sc["kind"]
            st = sc.get("state", {})
            # Convert lists back to numpy arrays where appropriate
            conv = {}
            for k, v in st.items():
                conv[k] = np.asarray(v, dtype=np.float32) if isinstance(v, (list, tuple)) else v
            obj._scaler_state_ = conv
            obj._scaler_spec_ = {"type": obj._scaler_kind_}
        return obj
