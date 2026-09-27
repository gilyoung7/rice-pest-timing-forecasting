# Handoff guide

Audience: the researcher/engineer taking over this project. Read README.md first.

## 1. What the system predicts

Rice pest occurrence timing for eight pests: WBPH, sheath_blight, bacterial_blight, brown_spot,
rice_stem_borer_1, rice_stem_borer_2, BPH, blast. For each (pest, site, year) the system issues an
alert and predicts the interval in which the pest occurrence falls. Evaluation is the 15-cell grid
**eval year ∈ {2022, 2023, 2024} × Stage-2 seed ∈ {0..4}** per pest; the headline metric is
`IoU80_overall_tol0` (15-cell macro; within a cell, the mean over 5 selector seeds).

All eight pests use the same canonical configuration, B + selector T, each with its own checkpoints
and Stage-1 dispatch. Canonical macros and status: README.md and `audit/CANONICAL_MULTIPEST.json`.
WBPH was canonical during the research; the other seven come from the preregistered cross-pest
frozen replication (2026-08-18) and were adopted as handoff canonical on 2026-09-27
(`docs/CANONICAL_MULTIPEST_DECISION.md`). BPH keeps its historical season window DOY 140–270 and is
not directly comparable with the DOY 60–300 pests.

WBPH progression (the other pests have the analogous D28 → D90 → B → T lineage in the crosspest report):

| model | 15-cell macro | status |
|---|---:|---|
| D28 (28-day context) | 0.3233107 | frozen reference |
| D90 (90-day monolithic context) | 0.3789493 | superseded paired control |
| B + selector v1 | 0.4496573 | superseded selector control |
| **B + selector T (v2)** | **0.5437853** | **canonical** (`audit/CANONICAL.json`) |

There is **no future-year holdout**: 2022–2024 numbers are selection-aware, temporally valid
development estimates, not test results (`audit/HOLDOUT_LOCK_AMENDMENT1_20260818.md`).

## 2. Pipeline

```
Stage 1 (XGBoost alert gate)          -- frozen; NOT rerun here
   └─ per-(site,year) dispatch features: rice/outputs/stage2/<batch>/WBPH/gate_*_R088_features_per_sy.csv
      (release asset; 2022: dispatch_group_tau, 2023: D_history, 2024: dispatch_group_tau)
Stage 2 "B" (scripts/run_expb_cell.sh → vendor/_patched_train.py → vendor/src/vendor/run_train.py)
   D28 encoder on the last 28 days + history encoder on days t−89..t−28 (d_model 48, 4 heads,
   1 layer) + zero-initialised sigmoid gate: z = h_r + g · W h_h, W = 0 at init.
   Same arguments as D90 (window 90, tstar_start 28, frozen D28 normalisation) + WBPH_EXPB_HISTORY_GATE=1.
   └─ checkpoint rice/outputs_allpests_e5d_expB_20260817/<y>/seed<s>/WBPH/clean/ckpt/<y>/ckpt/checkpoint_run4.pt
Grid (scripts/run_b_grid.sh → pest_grid.py → vendor/scripts/87_make_shared_offset_grid.py:collect)
   mu/sigma for candidate anchor offsets 1..75 → .../WBPH/clean/grid/WBPH_E5d_clean_grid_1to75.csv
Selector T (scripts/run_selector_t.sh → audit/selround1_20260818/run_selector_cell.py --arm T → pest_eval.py)
   LightGBM, 5 selector seeds, fit on the y−1 val_fit fold, shift calibrated on val_cal;
   features = official_v1 (22) + mu_position (WBPH_SELECTOR_ADD_MU_POSITION=1)
   └─ audit/selround1_20260818/runs/T/<y>/seed<s>/WBPH/{cell_result.json, eval/, selector_artifacts_v2/}
Aggregate (tools/aggregate_selector_cells.py) → outputs/selector_T_aggregate/{cells.csv, aggregate.json}
```

The seven other pests run the same stages with the pest as an argument:
`scripts/run_pest_b_grid.sh <pest>` (grid via `tools/pest_grid_reroot.py`, which maps the original
server's absolute dispatch path stored in the checkpoint into this repo and aborts on anything else),
`scripts/run_pest_selector_t.sh <pest>` (`tools/run_pest_selector_cell.py` with the frozen T env,
`tools/aggregate_pest_cells.py`). Their B checkpoints live under
`rice/outputs_crosspest_frozen_replication_20260818/B/<y>/seed<s>/<pest>/`, selector outputs under
`outputs/multipest/<pest>/`. For `WBPH` both launchers exec the original WBPH scripts unchanged.
Stage-1 dispatch is frozen for all pests; the tau actually used (`dispatch_tau_used`) is authoritative,
and 8 pest-years differ from the Stage-1 selection CSV (`manifests/multipest/STAGE1_OPERATING_POINTS.csv`).

Terminology traps:
- "T" is the treatment arm of selector round 1, i.e. selector v2 — not a model.
- `selector_artifacts_v2/` is an artifact *schema* version; it exists for both selector versions.
- The directory name `asym5_max140` = D28 (asym_weight 5.0, lead_max 140). D28/D90/B all use
  `asym_weight 5.0`; old READMEs mentioning 25.0 do not describe the canonical path.

## 3. Common tasks

| task | command | notes |
|---|---|---|
| reproduce one pest's headline from shipped checkpoints | `scripts/run_pest_b_grid.sh <pest> --check && scripts/run_pest_selector_t.sh <pest> --anchor` | ~20–40 min per pest on one RTX 4080; deterministic. WBPH: same as `scripts/run_b_grid.sh --check && scripts/run_selector_t.sh --anchor` |
| full gate run (G0–G3) for several pests | `scripts/run_multipest_acceptance.sh OUT_DIR [pest ...]` inside tmux | per-pest failure isolation; writes `OUT_DIR/summary.json` |
| input gate only | `PYTHONPATH=. .venv/bin/python tools/multipest_g0.py <pest>` | dispatch/climatology/raw sha, checkpoint metadata, D28 frozen-norm sha |
| retrain one WBPH B cell | `EXPB_DRY_RUN=1 scripts/run_expb_cell.sh 2022 0` then without `EXPB_DRY_RUN` | writes to `rice/outputs_expB_retrain/`; needs D90 args/splits + D28 checkpoints (release assets). No launcher is shipped for retraining the other pests; their D28/D90 inputs are in `<pest>_retrain.tar` and the executed driver is in the archive (`scripts/run_crosspest_frozen_cell.sh`) |
| check assets / data | `sha256sum -c manifests/RELEASE_ASSETS.sha256`, `manifests/multipest/RELEASE_ASSETS_<pest>.sha256`; see DATA.md | |

Long runs: use tmux with `scripts/tmux_terminal_wrapper.sh` (writes a terminal-state JSON and
signals `tmux wait-for`), and judge success only from exit code + required artifacts.

## 4. Reproducibility limits (read before trusting a rerun)

- Grid and selector are deterministic given a checkpoint (verified bitwise / ≤1e-12).
- **Training is not bitwise reproducible** (cuDNN non-deterministic algorithms; recorded in the
  code manifests). A retrained B will differ from the shipped checkpoints.
- Training-code provenance is proven only for `model.py`, `run_train.py`, `train_eval.py`
  (sha256 recorded in all 15 WBPH and all 105 crosspest checkpoints). Other training-path files are
  inferred unchanged. See PROVENANCE.md.
- Training was not re-executed during the handoff verification; Stage 1 was not re-run for any pest.
- The crosspest run recorded no grid sha256 at run time; the expected grid hashes were derived from
  the persisted grids at handoff (each equal to its independent selector-arm copy) and then
  reproduced bitwise in the acceptance.

## 5. Rules inherited from the project

- Do not modify the shipped canonical checkpoints, grids, anchors (WBPH and `audit/multipest/`) or
  decision records; record status changes as new history entries in `audit/CANONICAL_MULTIPEST.json`.
- `vendor/_patched_train.py` aborts canonical training when `RICE_DAILY_CSV` or
  `RICE_LONG_BY_PEST_DIR` is set; relocate data with `RICE_DATA_ROOT` (or the `data/` symlink).
- The holdout-lock list (architecture, loss, metric, selector, seed ensemble, checkpoint
  selection, inference, bins) applies if independent future data is ever obtained.
- Never cite results listed in docs/KNOWN_INVALID_RESULTS.md.

## 6. Where everything else is

Everything not needed for B + T (Stage-1 training, D28/D90 training launchers, ablations,
mechanism battery, augmentation, deployment/LiteRT lineage) stays in the archive repository;
see PROVENANCE.md §1 and docs/EXPERIMENT_SUMMARY.md. The complete crosspest output directory
(all arms, selector outputs, logs) is the archive Release `provenance-crosspest-frozen-20260818`
(docs/MULTIPEST_DATA.md §4).
