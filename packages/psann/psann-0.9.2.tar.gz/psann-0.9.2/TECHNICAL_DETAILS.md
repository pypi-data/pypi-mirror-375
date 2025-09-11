# PSANN Technical Details

This document explains the core components of PSANN, the math behind the parameterized sine activation, stateful time-series extensions, episodic (HISSO) training with predictive extras, and a lightweight PSANN-based language model.

## 1) Parameterized Sine Activation

Given pre-activation vector z (e.g., z = xW + b), each unit outputs

    h = A · exp(-d · g(z)) · sin(f · z)

where A (amplitude), f (frequency), and d (decay) are learnable scalars per output feature. The decay function g(z) controls amplitude attenuation:

- abs: g(z) = |z|
- relu: g(z) = max(0, z)
- none: g(z) = 0 (no decay)

Parameterization

- A, f, d are stored in unconstrained space, mapped with softplus to keep them positive and stable; optional bounds are supported.
- Weight initialization uses SIREN-style heuristics to maintain gradient flow.

Intuition

- f controls oscillation frequency; A scales amplitude; d provides a stabilizing envelope.

## 2) PSANN Blocks and Networks

- PSANNBlock: Linear + SineParam. Optionally integrates a persistent state controller (see §3).
- PSANNNet: MLP stack of PSANNBlocks with a linear head.
- Convolutional variants (PSANNConv1d/2d/3d): ConvNd + activation across channels + optional global avg pool + linear head; with per-element (segmentation) mode, the head is a 1×1 ConvNd returning outputs at each position.

## 3) Persistent State for Time Series

Each PSANNBlock can maintain a per-feature amplitude-like state s that modulates activations over time. The state is updated from the magnitude of current activations and clipped.

Update (per feature)

    s_t ← ρ · s_{t-1} + (1−ρ) · β · E[|y_t|]
    s_t ← max_abs · tanh(s_t / max_abs)

where ρ ∈ (0,1) controls persistence, β scales updates, and max_abs bounds the state using smooth tanh saturation. Expectation E is over non-feature dims (batch/spatial).

Implementation

- During forward, state values scale activations. Proposed updates are deferred and committed after each optimizer step to avoid in-place autograd issues.
- `detach` controls whether the state participates in the graph (attached vs detached semantics).
- Reset policy: `state_reset ∈ {batch, epoch, none}` controls reset frequency; shuffling is disabled when state spans across batches.
- Streaming: `step(x_t, y_t=None, update=False)` performs one step; `predict_sequence_online` applies per-step updates to limit error compounding.

## 4) Multi-Dimensional Inputs

Two modes support general input shapes X ∈ R^{N×…}:

- Flattened MLP: flatten to (N, F).
- Preserve shape with ConvNd: channels-first internally; supports channels-first/last; optional per-element head.

Gaussian input noise can be scalar, per-feature (flattened size), or shaped tensor broadcastable to inputs.

## 5) Loss Functions

Built-in: mse/l2, l1/mae, smooth_l1, huber. Custom: pass a callable; reduction applied as configured (mean/sum/none).

## 6) Initialization and Stability

- Linear layers: SIREN-style uniform inits.
- Conv layers: analogous SIREN-style init using fan-in.
- Sine parameters are softplus-mapped; decay stabilizes large activations.
- State updates bounded by tanh; deferred application avoids in-place issues.

## 7) Research Directions

1. Frequency/Amplitude Scheduling & Priors: spectral regularization on f; parameter tying or gating over A,f,d.
2. Physics-Informed & Hybrid Models: constrain f,d to regimes (e.g., damped harmonic); couple with classical filters.
3. State Dynamics & RNN Hybrids: learn update coefficients; gated state; truncated BPTT and sequence-aware batching.
4. Spatial Models & Per-Element Outputs: deeper conv PSANNs with multi-scale features; attention over spatial tokens.
5. Representation Learning: self-supervised pretraining; frequency-domain pretexts.
6. Robustness & Calibration: OOD detection, uncertainty calibration.

## 8) Episodic Training (HISSO) and Predictive Extras

Certain tasks benefit from optimizing a horizon-informed objective over windows rather than pointwise losses. We provide Predictive Extras and HISSO training.

- Predictive Extras: per step, the model outputs `M + K` values (first M = primary outputs, last K = extras). Extras are transformed (e.g., `tanh`) and concatenated to inputs at the next step, enabling compact context propagation without explicit state.

- HISSO in API: `PSANNRegressor.fit(..., hisso=True, hisso_window=T)` builds an episodic trainer that
  - samples random starts to build `(B, T, F)` windows,
  - rolls the model step-by-step with extras feedback,
  - maximizes a differentiable reward over the episode (e.g., portfolio log-returns),
  - supports decayed input noise.

- LSM integration: pass `lsm` as a pretrained module (`LSM`, `LSMConv2d`), an expander (`LSMExpander`, `LSMConv2dExpander`) with optional pretraining epochs, or a `dict` of parameters — flattened inputs → `LSMExpander`, 2D conv inputs → `LSMConv2dExpander`.

## 9) PSANN-LM (Language Model)

A minimal LM pipeline on top of PSANN for next-token prediction in embedding space.

Components
- Tokenizer: `SimpleWordTokenizer` (whitespace + specials) with `fit/encode/decode`.
- Embedder: `SineTokenEmbedder(D)` produces sinusoidal token embeddings `e[i, d] = A[d] · sin(ω[d] · (i + offset) + φ[d])`; amplitude A[d], phase φ[d], and offset may be learned; ω follows a transformer-like schedule.
- Core: `PSANNNet` maps `[emb_t, extras_t] → [emb_{t+1}, extras_{t+1}]`.

Objective
- Sample windows of length `T` from the token stream.
- Predict next embedding and minimize MSE: `E[||ŷ_emb(t+1) − e(x_{t+1})||^2]`.
- Extras (optional) are passed forward auto-regressively.

Perplexity (optional)
- Estimate token distribution from predicted embeddings using cosine-similarity softmax over the embedding matrix (temperature τ),
- compute cross-entropy to the true next token on minibatches, and report `perplexity = exp(CE)` periodically.

Curriculum learning
- “Progressive span” reduces sampling to a growing prefix of the stream from `min_frac` → `max_frac` over a warmup, then full coverage.

Persistence
- `PSANNLanguageModel.save(path)` records tokenizer vocab, embedder state, PSANN weights, and LMConfig.
- `PSANNLanguageModel.load(path)` reconstructs the full pipeline and restores the vocab size needed for nearest-neighbor decoding.

Limitations
- The embedder is fixed during LM training by default to avoid target drift; joint training can be added by snapshotting targets or using a teacher buffer.
- More expressive decoders (learned projection, FAISS k-NN) can improve token selection.

## 10) API Pointers

See `docs/API.md` for the full user-facing API, including shapes, parameter groups, and save/load semantics.

