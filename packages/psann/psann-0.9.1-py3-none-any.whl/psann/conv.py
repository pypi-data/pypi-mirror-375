from __future__ import annotations

from typing import Optional, Sequence
import math

import torch
import torch.nn as nn

from .activations import SineParam
from .utils import init_siren_linear_


class _PSANNConvBlockNd(nn.Module):
    def __init__(
        self,
        conv: nn.Module,
        out_channels: int,
        *,
        act_kw: Optional[dict] = None,
        activation_type: str = "psann",
    ) -> None:
        super().__init__()
        self.conv = conv
        act_kw = dict(act_kw or {})
        activation_type = activation_type.lower()
        if activation_type == "psann":
            act_kw.setdefault("feature_dim", 1)  # channel dimension
            self.act = SineParam(out_channels, **act_kw)
        elif activation_type == "relu":
            self.act = nn.ReLU()
        elif activation_type == "tanh":
            self.act = nn.Tanh()
        else:
            raise ValueError("activation_type must be one of: 'psann', 'relu', 'tanh'")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.conv(x)
        return self.act(z)


def _init_siren_conv_(conv: nn.Module, *, is_first: bool, w0: float = 30.0) -> None:
    """Initialize a ConvNd layer following a SIREN-like heuristic.

    Uses fan-in = in_channels * prod(kernel_size) to compute bounds analogous to linear layers.
    """
    if not hasattr(conv, "weight"):
        return
    weight = conv.weight
    # kernel_size may be tuple
    if hasattr(conv, "kernel_size"):
        ks = conv.kernel_size
        if isinstance(ks, int):
            kprod = ks
        else:
            kprod = 1
            for k in ks:
                kprod *= k
    else:
        kprod = 1
    in_features = weight.shape[1] * max(1, kprod)
    bound = (1.0 / in_features) if is_first else (math.sqrt(6.0 / in_features) / max(w0, 1e-6))
    torch.nn.init.uniform_(weight, -bound, bound)
    if getattr(conv, "bias", None) is not None:
        torch.nn.init.uniform_(conv.bias, -bound, bound)


class PSANNConv1dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        activation_type: str = "psann",
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv1d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw, activation_type=activation_type)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv1d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool1d(1)
            self.fc = nn.Linear(c, out_dim)
        # Initialization
        if hidden_layers > 0:
            # First conv as first, others as deeper
            _init_siren_conv_(self.body[0].conv, is_first=True, w0=w0)
            for blk in list(self.body)[1:]:
                _init_siren_conv_(blk.conv, is_first=False, w0=w0)
        if segmentation_head:
            _init_siren_conv_(self.head, is_first=False, w0=w0)
        else:
            init_siren_linear_(self.fc, is_first=False, w0=w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, L)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, L)
        x = self.pool(x).squeeze(-1)  # (N, C)
        return self.fc(x)


class PSANNConv2dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        activation_type: str = "psann",
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv2d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw, activation_type=activation_type)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv2d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool2d(1)
            self.fc = nn.Linear(c, out_dim)
        # Initialization
        if hidden_layers > 0:
            _init_siren_conv_(self.body[0].conv, is_first=True, w0=w0)
            for blk in list(self.body)[1:]:
                _init_siren_conv_(blk.conv, is_first=False, w0=w0)
        if segmentation_head:
            _init_siren_conv_(self.head, is_first=False, w0=w0)
        else:
            init_siren_linear_(self.fc, is_first=False, w0=w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, H, W)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, H, W)
        x = self.pool(x).flatten(1)  # (N, C)
        return self.fc(x)


class PSANNConv3dNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_dim: int,
        *,
        hidden_layers: int = 2,
        hidden_channels: int = 64,
        kernel_size: int | Sequence[int] = 1,
        act_kw: Optional[dict] = None,
        activation_type: str = "psann",
        w0: float = 30.0,
        segmentation_head: bool = False,
    ) -> None:
        super().__init__()
        ks = kernel_size if isinstance(kernel_size, int) else int(kernel_size[0])

        layers = []
        c = in_channels
        for i in range(hidden_layers):
            conv = nn.Conv3d(c, hidden_channels, kernel_size=ks, padding=(ks // 2 if ks > 1 else 0))
            block = _PSANNConvBlockNd(conv, hidden_channels, act_kw=act_kw, activation_type=activation_type)
            layers.append(block)
            c = hidden_channels
        self.body = nn.Sequential(*layers)
        self.segmentation_head = segmentation_head
        if segmentation_head:
            self.head = nn.Conv3d(c, out_dim, kernel_size=1)
        else:
            self.pool = nn.AdaptiveAvgPool3d(1)
            self.fc = nn.Linear(c, out_dim)
        # Initialization
        if hidden_layers > 0:
            _init_siren_conv_(self.body[0].conv, is_first=True, w0=w0)
            for blk in list(self.body)[1:]:
                _init_siren_conv_(blk.conv, is_first=False, w0=w0)
        if segmentation_head:
            _init_siren_conv_(self.head, is_first=False, w0=w0)
        else:
            init_siren_linear_(self.fc, is_first=False, w0=w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (N, C, D, H, W)
        if len(self.body) > 0:
            x = self.body(x)
        if self.segmentation_head:
            return self.head(x)  # (N, out_dim, D, H, W)
        x = self.pool(x).flatten(1)  # (N, C)
        return self.fc(x)
