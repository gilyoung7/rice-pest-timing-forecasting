# Rice pest occurrence-timing forecast — canonical handoff

Minimal, verified code to reproduce the canonical result of the WBPH (white-backed planthopper)
two-stage occurrence-timing forecaster:

**Canonical = Stage-2 model "B" + selector "T" (selector v2)** —
headline `IoU80_overall_tol0`, 15-cell macro (eval years 2022–2024 × Stage-2 seeds 0–4) =
**0.5437853333333333**.

This repository was assembled from exact git blobs of the research (archive) repository and
re-verified: all 15 B grids regenerate bitwise-identically and all 15 selector-T cells match the
canonical anchor within 1e-12 (see [PROVENANCE.md](PROVENANCE.md)).

## Quick start (reproduce the headline number)

```bash
# 1. environment (see ENVIRONMENT.md)
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.lock

# 2. raw data (see DATA.md): make data/ point at the shared data root
ln -s /path/to/shared/ygdata data            # needs data/rice/<daily csv>, data/rice/LONG_by_pest/
(cd data && sha256sum -c "$OLDPWD/manifests/RAW_DATA.sha256")

# 3. release assets (checkpoints, splits, dispatch inputs, reference grids)
for t in b_checkpoints_splits d28_frozen_norm_checkpoints d90_train_args_splits \
         stage2_dispatch_climatology reference_grids; do tar -xf /path/to/assets/$t.tar; done
sha256sum -c manifests/RELEASE_ASSETS.sha256

# 4. regenerate the 15 B grids and check them (G1), then selector T + anchor gate (G2/G3)
scripts/run_b_grid.sh --check
scripts/run_selector_t.sh --anchor
```

GPU required for step 4 (grid forward). The first grid run builds a ~5 GB preprocessing cache
under `rice/outputs/cache/` (regenerable, not shipped).

## Layout

| path | content |
|---|---|
| `rice/` | pipeline code, original module layout kept (`rice.src`, `rice.scripts`, `rice.configs`, `rice.pests.WBPH`) |
| `rice/experiments/allpests_e5d/` | Stage-2 E5d driver: `pest_grid.py`, `pest_eval.py`, `vendor/` (model + trainer) |
| `audit/selround1_20260818/run_selector_cell.py` | unchanged per-cell selector runner (path kept: it resolves the repo root from its location) |
| `scripts/` | `run_b_grid.sh`, `run_selector_t.sh`, `run_expb_cell.sh` (retraining), `tmux_terminal_wrapper.sh` |
| `tools/aggregate_selector_cells.py` | deterministic 15-cell aggregate + anchor gate |
| `audit/` | canonical decision records (verbatim) and `canonical_anchor.json` |
| `manifests/` | code provenance, release-asset and data sha256 lists |
| `docs/` | experiment summary, known invalid results, research direction |

## Read next

[HANDOFF.md](HANDOFF.md) (pipeline and how to work with it) · [DATA.md](DATA.md) ·
[ENVIRONMENT.md](ENVIRONMENT.md) · [PROVENANCE.md](PROVENANCE.md) ·
[docs/EXPERIMENT_SUMMARY.md](docs/EXPERIMENT_SUMMARY.md) ·
[docs/KNOWN_INVALID_RESULTS.md](docs/KNOWN_INVALID_RESULTS.md)
