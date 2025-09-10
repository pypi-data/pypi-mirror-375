# PSANN API Reference

This document summarizes the public, user-facing API of `psann` with shapes and key semantics.

## psann.PSANNRegressor

Sklearn-style estimator wrapping PSANN networks (MLP and Conv variants).

Constructor (key groups):

- Architecture
  - `hidden_layers: int = 2` — number of blocks.
  - `hidden_width: int = 64` — features/channels per hidden block.
  - `w0: float = 30.0` — SIREN-style init scale.
  - `activation: ActivationConfig | None` — config forwarded to `SineParam`.
  - `activation_type: str = 'psann'|'relu'|'tanh'` — nonlinearity per block.
- Training
  - `epochs: int = 200`, `batch_size: int = 128`, `lr: float = 1e-3`.
  - `optimizer: 'adam'|'adamw'|'sgd'`, `weight_decay: float = 0.0`.
  - `loss: str|callable` — `'mse'|'l1'|'smooth_l1'|'huber'` or a callable.
  - `loss_params: dict|None`, `loss_reduction: 'mean'|'sum'|'none'`.
  - `early_stopping: bool = False`, `patience: int = 20`.
- Runtime
  - `device: 'auto'|'cpu'|'cuda'|torch.device`, `random_state: int|None`.
  - `num_workers: int = 0` (DataLoader workers).
- Multi-D handling
  - `preserve_shape: bool = False` — conv body instead of flattening.
  - `data_format: 'channels_first'|'channels_last'` (when preserve_shape).
  - `conv_kernel_size: int = 1` — kernel size for conv blocks.
  - `per_element: bool = False` — segmentation-style head for per-position outputs.
  - `output_shape: tuple[int,...]|None` — target vector shape (pooled head only).
- Stateful (time series)
  - `stateful: bool = False` – enable per-feature persistent state.
  - `state: dict|None` – `{init,rho,beta,max_abs,detach}` config; required to enable.
  - `state_reset: 'batch'|'epoch'|'none'` – reset frequency during training.
  - `stream_lr: float|None` – LR for `step(..., update=True)` online updates.
- LSM integration
  - `lsm: dict|LSMExpander|LSMConv2dExpander|nn.Module|None` – expander/preprocessor. If a `dict` is provided, an appropriate expander is constructed (`LSMExpander` for flattened inputs; `LSMConv2dExpander` for 2D conv inputs). Keys map to respective constructor arguments like `output_dim/out_channels`, `hidden_layers`, `hidden_width/hidden_channels`, `sparsity`, `nonlinearity`, etc.
  - `lsm_train: bool = False` – jointly train LSM with PSANN (flattened path only).
  - `lsm_pretrain_epochs: int = 0` – optional pretrain epochs for `LSMExpander`.
  - `lsm_lr: float|None` – optional separate LR for LSM params when joint.
 - Extras/HISSO
  - `extras: int = 0` – number of “predictive extras” outputs appended after primary outputs when using episodic HISSO training.
 - Warm start
  - `warm_start: bool = False` – reuse existing `model_` weights across consecutive `fit()` calls when dimensions are compatible (incremental updates).

Methods:

- `fit(X, y=None, *, validation_data=None, verbose=0, noisy=None, hisso=False, hisso_window=None, hisso_reward_fn=None, hisso_context_extractor=None, hisso_trans_cost=None)`
  - Shapes:
    - Flattened: `X (N, F1,...,Fk)` flattened to `(N, prod(F*))`.
    - Preserve-shape: `X (N, C, ...)` or `(N, ..., C)` per `data_format`.
    - Targets: pooled `(N, T)`/`(N,)` or per-element `(N, C_out, ...)`/`(N, ..., C_out)`.
  - `noisy`: Gaussian input noise std – scalar, per-feature vector, or per-tensor std.
  - `hisso`: when True, performs episodic Horizon-Informed Sampling Strategy Optimization (HISSO). Uses a predictive-extras rollout under the hood with `extras` additional outputs; `y` is ignored. Primary outputs default to `X.shape[1]`.
  - `hisso_window`: episode/window length (defaults to 64 if not provided).
  - `hisso_reward_fn`: optional callable `(allocations: Tensor(B,T,M), context: Tensor(B,T,...) ) -> Tensor(B,)` to customize the episodic reward.
  - `hisso_context_extractor`: optional callable mapping X episodes to reward context (defaults to identity).
  - `hisso_trans_cost`: optional float (for the default portfolio reward when used).

- `predict(X) -> ndarray`
  - Pooled/vector head: `(N,)` if single target else `(N, T)`.
  - Per-element: preserves spatial dims; channels per `data_format`.

- `score(X, y) -> float`
  - R^2 via scikit-learn when available; simple fallback otherwise.

- `hisso_infer_series(X_obs, E0=None) -> (allocations, extras)`
  - Available after `fit(..., hisso=True)`. Rolls out primary allocations `(N, M)` and extras `(N+1, K)` over the entire series.

- `hisso_evaluate_reward(X_obs, n_batches=8) -> float`
  - Average episodic reward over random windows using the trained HISSO model.

- `reset_state()`
  - Reset persistent state values (when stateful with a state config).

- `step(x_t, y_t=None, update=False) -> float|ndarray`
  - Single-step forward; optionally apply immediate parameter update using `y_t`.
  - Returns scalar for single-target, or 1D array for multi-target.

- `predict_sequence(X_seq, *, reset_state=True, return_sequence=False) -> ndarray`
  - Free-run over a sequence; returns last prediction or the full sequence.

- `predict_sequence_online(X_seq, y_seq, *, reset_state=True) -> ndarray`
  - Per-step online updates using true targets to limit error compounding.

- `save(path)` / `load(path)`
  - Saves model weights and estimator params. Custom `loss` and attached `lsm` are not serialized; `load()` restores the network and basic metadata.

## psann.SineParam

Sine activation with per-feature learnable `amplitude`, `frequency`, and `decay`.

Constructor:

- `out_features: int`, `amplitude_init=1.0`, `frequency_init=1.0`, `decay_init=0.1`
- `learnable=('amplitude','frequency','decay')|str`, `decay_mode='abs'|'relu'|'none'`
- `bounds={'amplitude': (lo, hi), ...}`, `feature_dim=-1` (broadcast axis)

Forward: `A * exp(-d * g(z)) * sin(f * z)` with broadcasted parameters.

## LSM Expanders

- `LSM(input_dim, output_dim, *, hidden_layers=2, hidden_width=128, sparsity=0.8, nonlinearity='sine')`
  - Feed-forward sparse expander: `forward(X)` returns expanded features.

- `LSMExpander(output_dim, *, hidden_layers=2, hidden_width=128, sparsity=0.8, nonlinearity='sine', epochs=100, lr=1e-3, ridge=1e-4, ...)`
  - `fit(X)`, `transform(X)`, `fit_transform(X)`, `score_reconstruction(X)`.

- `LSMConv2d(in_channels, out_channels, *, hidden_layers=1, hidden_channels=128, kernel_size=1, sparsity=0.8, nonlinearity='sine')`

- `LSMConv2dExpander(out_channels, *, hidden_layers=1, hidden_channels=128, kernel_size=1, sparsity=0.8, epochs=50, lr=1e-3, ridge=1e-4, ...)`
  - Channel-preserving expansion for images; OLS readout trained in-loop.

Notes:

- When attaching an expander via `PSANNRegressor(lsm=..., lsm_train=False)`, features are precomputed once and fed to PSANN.
- Set `lsm_train=True` to jointly fine-tune the expander with PSANN (flattened inputs only).
- You can pass a `dict` as `lsm` and PSANN will build and (optionally) pretrain the expander internally.

## psann.PSANNLanguageModel and utilities

- `SimpleWordTokenizer`: whitespace tokenizer with `<PAD>`, `<UNK>`, `<BOS>`, `<EOS>`; `fit/encode/decode`, `vocab_size`.
- `SineTokenEmbedder(D)`: sinusoidal embeddings with optional learnable amplitude/phase; `set_vocab_size(V)` and `embedding_matrix()`.
- `PSANNLanguageModel`:
  - `fit(corpus, *, epochs=50, lr=1e-3, noisy=None, verbose=1, ppx_every=None, ppx_temperature=None, curriculum_type=None, curriculum_warmup_epochs=None, curriculum_min_frac=None, curriculum_max_frac=None)`
  - `predict(text, *, return_embedding=False)` → string or embedding
  - `generate(prompt, *, max_tokens=20)` (alias: `gen`)
  - `save(path)` / `load(path)`
  - Config via `LMConfig(embedding_dim, extras_dim, episode_length, batch_episodes, random_state, ppx_every, ppx_temperature, curriculum_*)`
