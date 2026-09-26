# Environment

## Python packages

`requirements.lock` is the exact `pip freeze --all` of the venv used for the 2026-09-26 canonical
reproduction (G1/G2/G3 passed). Key versions:

| package | version |
|---|---|
| Python | 3.12.3 |
| torch | 2.5.1+cu121 (from `https://download.pytorch.org/whl/cu121`) |
| numpy | 2.4.4 |
| pandas | 2.2.3 |
| scikit-learn | 1.7.2 |
| scipy | 1.17.1 |
| lightgbm | 3.3.5 |
| pyarrow | 25.0.1 |

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock
```

The venv must be at `<repo>/.venv`: `common.sh` and `run_selector_cell.py` call
`<repo>/.venv/bin/python`.

Do **not** use `rice/experiments/allpests_e5d/requirements.txt` from the archive repository: it
pins cu118 / lightgbm 4.5.0 / numpy 1.26, which is not the environment that produced the
canonical result. The selector depends on LightGBM, so a different LightGBM version may change
selector T results.

## Non-pip environment (verified run)

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
- Grid generation and selector T were bitwise / ≤1e-12 reproducible on the verified environment.
  A different GPU, driver or library version may change grid bytes; re-run the G1–G3 gates
  (PROVENANCE.md §4) after any environment change.
- Recommended variables for the canonical scripts are set inside them
  (`PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled MPLBACKEND=Agg`, e5d env from `common.sh`).
