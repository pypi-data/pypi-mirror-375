# PSANN Technical Details

This document explains the core components of PSANN, the math behind the sine activation with learned parameters, the stateful time-series extensions, and directions for further research.

## 1) Parameterized Sine Activation

Given a pre-activation vector z (e.g., z = xW + b), the unit output is

    h = A · exp(−d · g(z)) · sin(f · z)

where A (amplitude), f (frequency), and d (decay) are learnable scalars per output feature (neuron). The decay function g(·) controls how amplitude diminishes with activation magnitude:

- abs: g(z) = |z|
- relu: g(z) = max(0, z)
- none: g(z) = 0 (no decay)

Parameterization:

- A, f, d are stored in an unconstrained space and mapped through softplus to keep them positive and stable.
- Optional bounds clamp values post-transform.
- Weight initialization uses SIREN-style heuristics to maintain gradient flow at start.

Intuition:

- f scales oscillation, A scales amplitude, and d adds an envelope that attenuates with |z| (or only for positive z via relu), which helps stabilize extreme activations and encourages compact representations of oscillatory signals.

## 2) PSANN Blocks and Networks

- PSANNBlock: Linear -> SineParam. Optionally integrates a persistent state controller (see §3).
- PSANNNet: MLP stack of PSANNBlocks with a linear head.
- Conv variants (PSANNConv1d/2d/3d): ConvNd -> SineParam across channels -> optional global average pool -> linear head. With per-element (segmentation) mode, the head is a 1×1 ConvNd returning outputs at each position.

## 3) Persistent State for Time Series

Each PSANNBlock can maintain a per-feature “amplitude-like” state s that modulates activations over time. The state is updated from the magnitude of the current activations and clipped to avoid explosion.

Update rule per feature:

    s_t ← ρ · s_{t−1} + (1 − ρ) · β · E[|y_t|]
    s_t ← max_abs · tanh(s_t / max_abs)

where ρ ∈ (0, 1) controls persistence, β scales updates, and max_abs bounds the state using a smooth tanh saturation. The expectation E is taken over non-feature dimensions (batch/spatial), producing a feature-wise update.

Implementation details:

- During forward, state values are used to scale activations. Parameter updates to the state are deferred and committed safely after each optimizer step to avoid autograd in-place issues.
- A detach flag controls whether the state used for scaling participates in the computation graph (attached vs detached semantics).
- Training reset policy: `state_reset` ∈ {batch, epoch, none} controls reset frequency; shuffling is disabled when state spans across batches.

Streaming API:

- step(x_t, y_t=None, update=False): emits a prediction and (optionally) performs an immediate gradient update using the provided target while keeping the current state (no additional state update during the gradient pass).
- predict_sequence_online(X_seq, y_seq): iterates over a sequence, applying per-step updates to prevent error compounding.

## 4) Multi-Dimensional Inputs

Two modes support general input shapes X ∈ R^{N×…}:

- Flattened MLP: flatten features to (N, F).
- Preserve shape with ConvNd: channels-first internal layout; supports both channels-first and channels-last inputs; optional per-element head.

Gaussian input noise for regularization can be scalar, per-feature vector (flattened size), or a tensor matching the original feature shape (broadcasted appropriately in both modes).

## 5) Loss Functions

Built-in: mse/l2, l1/mae, smooth_l1 (β), huber (δ).
Custom: pass a callable loss that returns a tensor or scalar; reduction is applied as configured (mean/sum/none).

## 6) Initialization and Stability

- Linear layers use SIREN-inspired uniform inits to keep gradients healthy.
- Sine parameters are softplus-mapped; decay introduces a stabilizing envelope.
- State updates are bounded by tanh, and deferred application avoids in-place autograd issues.

## 7) Research Directions

1. Frequency/Amplitude Scheduling and Priors
   - Spectral regularization on f to bias networks toward certain frequency bands.
   - Parameter tying across layers or learned gating networks controlling A, f, d.

2. Physics-Informed and Hybrid Models
   - Constrain f and d to physical regimes (e.g., damped harmonic motion), or add physics penalties to the loss.
   - Couple PSANN blocks with classical filters (Kalman-like) or ARIMA components.

3. State Dynamics and RNN Hybrids
   - Learn the state update (ρ, β, max_abs) or replace it with a tiny gated network.
   - Truncated BPTT windows with sequence-aware batching and curriculum schedules.

4. Spatial Models and Per-Element Outputs
   - Deeper conv PSANNs with multi-scale features; attention over spatial tokens.
   - Segmentation and dense forecasting with spatiotemporal consistency regularizers.

5. Representation Learning
   - Self-supervised objectives (contrastive/predictive coding) before fine-tuning.
   - Frequency-domain pretext tasks to align sine parameters to data spectra.

6. Robustness and Calibration
   - Uncertainty estimation (ensembles, MC dropout) for time-series forecasts.
   - Robust losses (Huber variants) and constraints to mitigate drift.

7. Deployment and Acceleration

   - torch.compile/ONNX export; kernel fusion for sine + exp; quantization-aware training.

## 8) Practical Guidance

- Start with modest hidden width (32–128) and 2–3 layers; tune f and d in activation config for your domain.
- For long sequences, prefer detached state during streaming; use `stream_lr` lower than training `lr`.
- When preserving shape, begin with `conv_kernel_size=1` and widen channels before increasing kernel size.
- Prefer SmoothL1/Huber on noisy targets.

---

## 9) Parameter Reference

This section summarizes initializer parameters for exposed classes and how they interact.

### psann.activations.SineParam

- out_features: number of output units for the preceding linear/conv op.
- amplitude_init, frequency_init, decay_init: positive initial values (mapped via softplus internally).
- learnable: which of {"amplitude","frequency","decay"} are trainable; accepts tuple or "all"/"none".
- decay_mode: one of {"abs","relu","none"}; controls envelope g(z).
- bounds: optional dict, e.g., {"amplitude": (lo, hi), "frequency": (lo, hi), "decay": (lo, hi)} applied post-softplus.
- feature_dim: axis along which features/channels lie for broadcasting (e.g., 1 for channels-first, -1 for last).

### psann.state.StateController (used by PSANNBlock when stateful)

- init: initial state value (default 1.0).
- rho: persistence in [0,1]; higher = longer memory.
- beta: update scale from |activation|.
- max_abs: clipping bound applied via tanh for stability.
- detach: if True, forward scaling uses a detached copy (no BPTT through state); updates are deferred and committed.

### psann.nn.PSANNBlock

- in_features, out_features: linear projection size.
- act_kw: dict forwarded to SineParam (see above).
- state_cfg: optional dict forwarded to StateController to enable persistent state.

### psann.nn.PSANNNet

- input_dim, output_dim: flat input/output sizes.
- hidden_layers: number of PSANNBlock layers.
- hidden_width: width for each hidden block.
- act_kw: SineParam config shared across blocks.
- state_cfg: StateController config; enables stateful units when set.
- w0: SIREN-style init parameter for linear layers.

### psann.conv.PSANNConv1dNet / PSANNConv2dNet / PSANNConv3dNet

- in_channels: input channels.
- out_dim: number of output targets (vector head) or channels (segmentation head).
- hidden_layers, hidden_channels: number of conv blocks and their channel width.
- kernel_size: convolutional kernel size (default 1 for 1×1 conv-like behavior).
- act_kw: SineParam config (applied over channels with feature_dim=1).
- w0: SIREN-style init.
- segmentation_head: if True, replaces global average pooling + linear head with 1×1 ConvNd producing per-element outputs.

### psann.sklearn.PSANNRegressor

- Architecture
  - hidden_layers, hidden_width: depth/width for MLP or conv body.
  - w0: SIREN-style init scale.
  - activation: dict forwarded to SineParam.
- Training
  - epochs, batch_size, lr, optimizer ("adam"|"adamw"|"sgd"), weight_decay.
  - loss: "mse"|"l1"/"mae"|"smooth_l1"|"huber" or a custom callable; loss_params, loss_reduction.
  - early_stopping: bool; patience.
  - verbose in fit(...): prints train/val loss each epoch.
  - noisy in fit(...): scalar or per-feature std; adds Gaussian noise to inputs each epoch.
- Runtime
  - device: "auto"|"cpu"|"cuda" or torch.device; num_workers for DataLoader.
  - random_state: for reproducible shuffles/inits.
- Multi-D handling
  - preserve_shape: if False (default) flatten features to (N,F); if True, use ConvNd stack preserving (N,C, ...).
  - data_format: "channels_first" or "channels_last" for preserved-shape mode.
  - conv_kernel_size: kernel size for PSANNConv blocks.
  - per_element: if True, use segmentation-style head for per-pixel/timestep outputs.
  - output_shape: desired output shape — for MLP/pooled head, prod(output_shape) == number of targets; for per-element, it determines channels.
- Stateful (time series)
  - stateful: enable StateController in hidden blocks.
  - state: dict {init,rho,beta,max_abs,detach}.
  - state_reset: "batch"|"epoch"|"none" — when to reset state during fit; order preserved when needed.
  - stream_lr: learning rate for online step() updates (defaults to lr).
  - Online APIs: step(x_t, y_t=None, update=False); predict_sequence(...); predict_sequence_online(X_seq, y_seq,...).
- LSM integration
  - lsm: an LSMExpander, LSMConv2dExpander, or a torch.nn.Module with output_dim/out_channels.
  - lsm_train: if True, jointly trains LSM and PSANN (on-the-fly transform); else precompute/transform once.
  - lsm_pretrain_epochs: when using an Expander, pre-fit epochs before PSANN training.
  - lsm_lr: optional separate LR for LSM parameters during joint training.

### psann.lsm.LSM (base MLP expander)

- input_dim, output_dim: expansion from D → K.
- hidden_layers, hidden_width: depth/width.
- sparsity: expected fraction of masked (zeroed) connections (0.8 → 80% masked, 20% density).
- nonlinearity: "sine"|"tanh"|"relu".
- bias: include bias terms; random_state for mask seeding.

### psann.lsm.LSMExpander (pretraining interface)

- Model/expansion
  - output_dim, hidden_layers, hidden_width, sparsity, nonlinearity.
- Optimization
  - epochs, lr, ridge (ridge-OLS readout), batch_size (currently full-batch used for OLS-in-the-loop).
  - device, random_state.
  - objective: "r2" (SSR/SST) or "mse".
  - noisy: scalar or per-feature std for input noise; noise_decay ∈ (0,1] for annealing each epoch.
  - Regularizers on Z: alpha_ortho (decorrelate channels), alpha_sparse (L1), alpha_var (variance target), target_var.
- Early stopping / validation
  - early_stopping: bool; patience; tol (min improvement in val R^2 to reset patience).
  - val_split: float in (0,1); or provide validation_data in fit().

### psann.lsm.LSMConv2d (conv expander)

- in_channels, out_channels: channel expansion.
- hidden_layers, hidden_channels: number and width of masked conv blocks.
- kernel_size: support k×k sparse convs; sparsity masks per kernel weight.
- nonlinearity: "sine"|"tanh"|"relu"; bias; random_state for masks.

### psann.lsm.LSMConv2dExpander (conv pretraining interface)

- Model/expansion
  - out_channels, hidden_layers, hidden_channels, kernel_size, sparsity, nonlinearity.
- Optimization
  - epochs, lr, ridge, device, random_state.
  - noisy: scalar or per-channel std (shape (C,) or (C,1,1)); noise_decay for annealing.
  - Regularizers on Z (flattened spatially): alpha_ortho, alpha_sparse, alpha_var, target_var.
- Note: operates on channels-first inputs (N,C,H,W); extends to 1D/3D analogously.
