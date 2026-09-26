# Provenance

## 1. Archive repository

This repository is a verified extract of the research repository, which remains the
authoritative record of the research process.

| item | value |
|---|---|
| archive remote | `git@github.com:gilyoung7/cropscience.git` |
| original checkout | `/home/gpu4080/research/cropscience_multipest` (branch `exp/clean2024-D-wbph-only`, HEAD `98f45dbc597f81ca8b5a3721540b53355467883e`) |
| experiment-hook snapshot | branch `snapshot/sept-experiment-hooks` @ `83dc4a392ca854c4838340e76d37f8df89d37777` (uncommitted Aug–Sep hooks + untracked sources/docs, INVALID markers, provenance manifests) |
| B training code tag | `canonical-B-train` (annotated tag object `3c57771e85faa84f00b1cf9798228b591fa81f4a` → commit `fec1409829e877da923b8e7de37cc659d2ef45b0`) |
| canonical outputs (archive) | `rice/outputs_allpests_e5d_expB_20260817` (B), `audit/selround1_20260818/runs/T` (selector T) |

## 2. Source recipe (authoritative)

| part | source |
|---|---|
| base | commit `fec1409` (all pipeline code, see `manifests/PROVENANCE.csv`) |
| override | `rice/scripts/eval_s2n_direct_compare.py` @ `7029760`, blob `7eb441cdafa05dc7184320950b937a3214156f3e` (history-gate support in `build_model`; the `fec1409` blob cannot load B checkpoints) |
| override | `rice/experiments/allpests_e5d/vendor/src/selector_utils.py` @ `7029760`, blob `5626d522e15fc244ad4e566fc58a0256177e60e5` (`mu_position`; absent from the selector-v2 commit `0ea9c60`) |
| selector cell runner | `audit/selround1_20260818/run_selector_cell.py` @ `0ea9c60`, blob `c86b365ea327e3a7f47e6ee9f60c4c952f169ca3` |
| `pest_eval.py` | `fec1409` blob `d4fac72ad2e7e867c5d135a9593be8d6ae3fc6a3` = executed blob (identical at `359cc47`, `0ea9c60`); the `7029760`/HEAD versions must not be used |
| `scripts/tmux_terminal_wrapper.sh` | `7029760` (utility; not part of any computation) |
| decision records under `audit/`, `docs/RESEARCH_DIRECTION_CORE.md` | archive HEAD `98f45db`, verbatim |
| excluded | `audit/selround1_20260818/finalize_selround1.py` (executed version unrecoverable), `run_selround1.sh` (calls it), `wandb_viz_e5d.py` (dev/W&B path only) |

## 3. Files changed during the handoff

Only paths/comments; no algorithm, hyperparameter, metric or data semantics changed.

| file | change |
|---|---|
| `rice/configs/base.py` | data defaults: absolute `/home/gpu4080/ygdata/...` → `RICE_DATA_ROOT` (default `<repo>/data`); `RICE_DAILY_CSV` / `RICE_LONG_BY_PEST_DIR` overrides unchanged |
| `rice/experiments/allpests_e5d/vendor/scripts/87_make_shared_offset_grid.py` | docstring usage example and the standalone-CLI constants `WS`/`CS` (env + relative default); `collect()` does not use them |
| `scripts/run_expb_cell.sh` | repo/D90/D28/output roots from env with repo-relative defaults; frozen-norm D28 path re-rooted at run time; `EXPB_DRY_RUN`; default output `rice/outputs_expB_retrain` |
| new | `scripts/run_b_grid.sh`, `scripts/run_selector_t.sh`, `tools/aggregate_selector_cells.py`, docs, manifests, `requirements.lock`, `.gitignore` |

`manifests/PROVENANCE.csv` lists every tracked file with its origin commit, source blob and
current blob; `verbatim` rows must hash to the source blob.

## 4. Verification history

**Archive verification (2026-09-26, `/home/gpu4080/research/repro_verify_B_T_20260926`)** on
`fec1409` + the overrides above (before the handoff path edits):

| gate | result |
|---|---|
| G1: 15 B grids regenerated from the B checkpoints, sha256 vs `audit/selround1_20260818/inputs_manifest.txt` | 15/15 bitwise identical |
| G2: selector T cells vs `audit/canonical_anchor.json` | 15/15, max abs delta 1.1e-16 (gate 1e-12) |
| G3: 15-cell macro | 0.5437853333333333 = anchor (delta 0.0) |

Supplementary: the 75 LightGBM selector models were byte-identical to the originals; selector
parquet artifacts differed only in the `output_root` column (absolute run location).

**Clean-repo acceptance (2026-09-26, r3, `/home/gpu4080/research/handoff_acceptance_20260926_r3`)**:
fresh clone of commit `91da3f749280903c1b967165d65b82eb405f96c1`; new `.venv` from `requirements.lock`
(sha256 `ef54b83a4195b1f59dcf661d73a65028c05f99ee999a197609c15de7adc9b650`) with the normal pip resolver;
release assets and raw data verified by sha256; preprocessing cache regenerated from raw data inside the
clone; everything outside the clone and the acceptance directory stayed read-only (0 writes).

| step | result |
|---|---|
| environment | `pip check` clean; 150 packages == lock; Python 3.12.3, torch 2.5.1+cu121, CUDA 12.1, cuDNN 90100, RTX 4080, driver 580.173.02 |
| inputs | release archives 5/5, release assets 216/216, reference grids 15/15, raw data 2/2 |
| cache | regenerated from raw data (key `0dcb950c71a6e151`, 5,286,866,957 B) |
| G1 | 15/15 grid SHA256 bitwise identical; cache diagnostic 30 hits / 0 misses |
| G2 | 15/15 cells, max abs delta 1.1e-16 (gate 1e-12) |
| G3 | macro 0.5437853333333333 (expected 0.5437853333333333, delta 0.0) |

The G1 stage first reported FAILED: an auxiliary cache-hit assertion expected 15 lines instead of
the actual 30 (each grid run loads the cache twice). The authoritative SHA gate had passed 15/15 in
that run; the assertion was corrected and re-evaluated from the original logs without recomputing
any grid. Earlier acceptance attempts r1 (unresolvable nccl pin in the lock) and r2 (wrong
reference-grid paths in `RELEASE_ASSETS.sha256`) failed before G1; both defects were fixed in
`f393878` and `91da3f7`. With this result the handoff environment (ENVIRONMENT.md) is the
authoritative installation environment of this repository.

Commits after `91da3f7` change documentation and manifests only (no executable code, no
checkpoint/asset content); the full acceptance above therefore applies to them without re-running
G1–G3. Verify with `git diff --stat 91da3f7 HEAD -- '*.py' '*.sh' rice/experiments/allpests_e5d/pests.tsv requirements.lock`
(expected: empty).

## 5. Manifests

| file | meaning |
|---|---|
| `manifests/B_GRID_CODE_MANIFEST.csv` | grid-stage code set, status VERIFIED by G1 (archive blobs; 87 later received the §3 path edit) |
| `manifests/SELECTOR_T_CODE_MANIFEST.csv` | selector T files: `provenance_basis` (recorded/inferred/unrecoverable) separate from `reproduction_status` (G2_VERIFIED …) |
| `manifests/PROVENANCE.csv` | every tracked file: origin, source commit/blob, current blob, sha256 |
| `manifests/B_GRID_SHA256.txt` | expected sha256 of the 15 canonical grids (from `inputs_manifest.txt`) |
| `manifests/RELEASE_ASSETS.sha256`, `RELEASE_ARCHIVES.sha256` | release-asset files and tarballs |
| `manifests/RAW_DATA.sha256` | the two raw data files |
| `manifests/EXTERNAL_DEPENDENCIES.csv` | everything outside git that the canonical path needs |

## 6. Known provenance limits

- B training: only `model.py`, `run_train.py`, `train_eval.py` were hashed at run time (15/15
  match `fec1409`); the other training-path files are inferred unchanged — whether the tree was
  dirty in those files on 2026-08-16 cannot be proven.
- Grid: the grid-stage code was not hashed at run time; its identity is established by G1.
- Selector: several files are `inferred` (single committed version); G2 verifies the file-version
  combination as a whole.
- The original `finalize_selround1.py` that wrote `cells.csv` is not in git; the canonical
  `cells.csv` equals the 45 per-cell `cell_result.json` values exactly.
