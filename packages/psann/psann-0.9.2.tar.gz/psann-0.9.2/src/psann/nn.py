from __future__ import annotations

from typing import Dict, Optional

import torch
import torch.nn as nn

from .activations import SineParam
from .utils import init_siren_linear_
from .state import StateController


class PSANNBlock(nn.Module):
    """Linear layer followed by parameterized sine activation.

    Optional per-feature persistent state acts as an amplitude modulator.
    """

    def __init__(self, in_features: int, out_features: int, *, act_kw: Optional[Dict] = None, state_cfg: Optional[Dict] = None, activation_type: str = "psann") -> None:
        super().__init__()
        act_kw = act_kw or {}
        self.linear = nn.Linear(in_features, out_features)
        self.activation_type = activation_type.lower()
        if self.activation_type == "psann":
            self.act = SineParam(out_features, **act_kw)
        elif self.activation_type == "relu":
            self.act = nn.ReLU()
        elif self.activation_type == "tanh":
            self.act = nn.Tanh()
        else:
            raise ValueError("activation_type must be one of: 'psann', 'relu', 'tanh'")
        self.state_ctrl = StateController(out_features, **state_cfg) if state_cfg else None
        self.enable_state_updates = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.linear(x)
        y = self.act(z)
        if self.state_ctrl is not None:
            update_flag = self.training and self.enable_state_updates
            y = self.state_ctrl.apply(y, feature_dim=1, update=update_flag)  # (N, F)
        return y


class PSANNNet(nn.Module):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_width: int = 64,
        act_kw: Optional[Dict] = None,
        state_cfg: Optional[Dict] = None,
        activation_type: str = "psann",
        w0: float = 30.0,
    ) -> None:
        super().__init__()
        act_kw = act_kw or {}

        layers = []
        prev = input_dim
        for i in range(hidden_layers):
            block = PSANNBlock(prev, hidden_width, act_kw=act_kw, state_cfg=state_cfg, activation_type=activation_type)
            layers.append(block)
            prev = hidden_width
        self.body = nn.Sequential(*layers)
        self.head = nn.Linear(prev, output_dim)

        # SIREN-inspired initialization
        if hidden_layers > 0:
            if isinstance(self.body[0], PSANNBlock):
                init_siren_linear_(self.body[0].linear, is_first=True, w0=w0)
            for block in list(self.body)[1:]:
                init_siren_linear_(block.linear, is_first=False, w0=w0)
        init_siren_linear_(self.head, is_first=False, w0=w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if len(self.body) > 0:
            x = self.body(x)
        return self.head(x)

    def reset_state(self) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock) and getattr(m, "state_ctrl", None) is not None:
                # reset to 1.0 by default
                m.state_ctrl.reset_like_init(1.0)

    def commit_state_updates(self) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock) and getattr(m, "state_ctrl", None) is not None:
                m.state_ctrl.commit()

    def set_state_updates(self, enabled: bool) -> None:
        for m in self.modules():
            if isinstance(m, PSANNBlock):
                m.enable_state_updates = bool(enabled)


class WithPreprocessor(nn.Module):
    """Wrap a preprocessor module with a core predictor.

    - preproc: optional nn.Module applied to inputs first (e.g., LSM/LSMConv2d)
    - core: PSANNNet or PSANNConvNdNet that consumes the preprocessed features

    Methods like reset_state/commit_state_updates/set_state_updates are
    forwarded to the core if present.
    """

    def __init__(self, preproc: nn.Module | None, core: nn.Module) -> None:
        super().__init__()
        self.preproc = preproc if preproc is not None else None
        self.core = core

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = x if self.preproc is None else self.preproc(x)
        return self.core(z)

    # Stateful helpers are delegated to core if available
    def reset_state(self) -> None:
        if hasattr(self.core, "reset_state"):
            self.core.reset_state()

    def commit_state_updates(self) -> None:
        if hasattr(self.core, "commit_state_updates"):
            self.core.commit_state_updates()

    def set_state_updates(self, enabled: bool) -> None:
        if hasattr(self.core, "set_state_updates"):
            self.core.set_state_updates(enabled)
