# Environment

## Two different environments — do not confuse them

| | original research environment | handoff environment (`requirements.lock`) |
|---|---|---|
| role | produced the canonical checkpoints (2026-08-16) and the archive re-verification (2026-09-26) | clean, resolver-consistent reproduction environment for this repository |
| where | the lab server's venv (`/home/gpu4080/research/cropscience/.venv`) | built from `requirements.lock` with the normal pip resolver |
| torch | 2.5.1+cu121 | 2.5.1+cu121 |
| nvidia-nccl-cu12 | **2.30.4** | **2.21.5** (the version torch 2.5.1+cu121 requires) |
| xgboost / lightgbm / numpy / pandas / scikit-learn / scipy / pyarrow | 3.0.5 / 3.3.5 / 2.4.4 / 2.2.3 / 1.7.2 / 1.17.1 / 25.0.1 | same |
| all other packages (150 total) | — | same versions as the original `pip freeze --all` |
| `pip check` | **fails**: torch requires nccl 2.21.5 but 2.30.4 is installed (xgboost 3.0.5 had pulled it) | clean |
| canonical reproduction | G1/G2/G3 PASS in the archive verification tree | acceptance status: see PROVENANCE.md §4 |

The original environment is not reproducible with a normal resolver and is intentionally not
recreated. Use the handoff environment:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock     # normal resolver; do not use --no-deps
.venv/bin/pip check                            # must report no broken requirements
```

Key versions: Python 3.12.3, torch 2.5.1+cu121 (`https://download.pytorch.org/whl/cu121`),
numpy 2.4.4, pandas 2.2.3, scikit-learn 1.7.2, scipy 1.17.1, lightgbm 3.3.5, pyarrow 25.0.1,
xgboost 3.0.5 (imported by `rice/scripts/run_event_train.py`).

The venv must be at `<repo>/.venv`: `common.sh` and `run_selector_cell.py` call
`<repo>/.venv/bin/python`.

Do **not** use `rice/experiments/allpests_e5d/requirements.txt` from the archive repository: it
pins cu118 / lightgbm 4.5.0 / numpy 1.26, which is not the environment that produced the
canonical result. The selector depends on LightGBM, so a different LightGBM version may change
selector T results.

## Non-pip environment (lab server used for both verifications)

| item | value |
|---|---|
| GPU | NVIDIA GeForce RTX 4080 (single GPU) |
| NVIDIA driver | 580.173.02 |
| CUDA runtime (torch) | 12.1 |
| cuDNN (torch) | 9.1.0 (90100) |
| OS | Linux 7.0.0-28-generic x86_64, glibc 2.39 |

The canonical training run (2026-08-16) recorded the same Python/torch/CUDA/cuDNN/package
versions in its code manifests; the driver version at that time was not recorded.

## Determinism

- Code manifests record `deterministic_algorithms=False`, `cudnn_deterministic=False`:
  training is not bitwise reproducible.
- Grid generation and selector T were bitwise / ≤1e-12 reproducible in the archive verification
  (original research environment); for the handoff environment see PROVENANCE.md §4.
  A different GPU, driver or library version may change grid bytes; re-run the G1–G3 gates
  (PROVENANCE.md §4) after any environment change.
- Recommended variables for the canonical scripts are set inside them
  (`PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled MPLBACKEND=Agg`, e5d env from `common.sh`).
