# Data and artifacts

Nothing below is stored in git. The repo only carries the sha256 lists in `manifests/`.

## 1. Raw data (shared storage; not redistributed)

Canonical B + T reads exactly two raw files. Place (or symlink) the data root at `data/`,
or set `RICE_DATA_ROOT` to it. The layout under the root is the original server's
`ygdata/` layout.

| path under data root | size | sha256 | used by |
|---|---:|---|---|
| `rice/1997_2024_RICE_union_all_sites_with_GDD10_since_gs.csv` | 1,723,783,551 B | `6be32990981ce984c71eccb9c8ed21e1ccbc5eed21fc43c9a0fe210afc7c12d8` | daily weather features (`rice/configs/base.py: PATH_DAILY`) |
| `rice/LONG_by_pest/RICE_LONG_흰등멸구.csv` | 8,204,659 B | `3b1b6bc61cb9cc442b4466b56e91fb633e4b146a5bae67f8155cc45f8e5bfac5` | WBPH occurrence labels (`rice/pests/WBPH/config.py: PATH_OBS`) |

Original location (first server): `/home/gpu4080/ygdata/rice/…`. Check after placing:

```bash
(cd data && sha256sum -c "$OLDPWD/manifests/RAW_DATA.sha256")
```

`RICE_DAILY_CSV` / `RICE_LONG_BY_PEST_DIR` still override single paths, but canonical training
(`vendor/_patched_train.py`) aborts when they are set — use `RICE_DATA_ROOT`.

## 2. Release assets (GitHub Release of this repo)

Deterministic tarballs with repo-relative paths; extract at the repo root. Per-file sha256:
`manifests/RELEASE_ASSETS.sha256` (216 files); archive sha256: `manifests/RELEASE_ARCHIVES.sha256`.

| asset | files | extracts to | needed for |
|---|---:|---|---|
| `b_checkpoints_splits.tar` (17 MB) | 120 | `rice/outputs_allpests_e5d_expB_20260817/<y>/seed<s>/WBPH/clean/{ckpt/<y>/…, split_*}` | grid, selector (inference/eval) |
| `d28_frozen_norm_checkpoints.tar` (12 MB) | 15 | `rice/outputs_allpests_e5d_asym5_max140_20260804/…/checkpoint_run4.pt` | B retraining only (frozen normalisation); sha256 also in `audit/d28_frozen_manifest.txt` |
| `d90_train_args_splits.tar` (0.6 MB) | 60 | `rice/outputs_allpests_e5d_d90_20260814/<y>/seed<s>/WBPH/clean/{ckpt/<y>/train_args.txt, split_*}` | B retraining only (argument template + splits) |
| `stage2_dispatch_climatology.tar` (1.8 MB) | 6 | `rice/outputs/stage2/<batch>/WBPH/{gate_*_R088_features_per_sy.csv, climatology_train_stats.csv}` | training, grid, selector |
| `reference_grids.tar` (21 MB) | 15 | `reference/grids/<y>/seed<s>/WBPH_E5d_clean_grid_1to75.csv` | reference only (G1 uses `manifests/B_GRID_SHA256.txt`) |

Notes:
- Extract at the repo root; the launchers then find everything by default. Optional overrides:
  `B_ROOT` (`scripts/run_b_grid.sh`), `D90_ROOT` / `D28_ROOT` / `EXPB_OUT_ROOT`
  (`scripts/run_expb_cell.sh`), `REPO_ROOT` (all launchers). `run_selector_cell.py` always reads
  the B assets from `rice/outputs_allpests_e5d_expB_20260817/`. Full table:
  `manifests/EXTERNAL_DEPENDENCIES.csv`.
- The B checkpoint directories intentionally contain **no grid**: `scripts/run_b_grid.sh`
  regenerates it there, and `run_selector_cell.py` reads it from there.
- `rice/outputs_stage2_batch_*` are tracked symlinks to `outputs/stage2/<batch>`; checkpoint
  arguments reference dispatch CSVs through those relative paths.
- `train_args.txt` / `hparams.json` inside the assets still contain absolute paths of the
  original server (e.g. the frozen-norm D28 checkpoint). They are provenance and are not edited;
  `scripts/run_expb_cell.sh` re-roots the frozen-norm path under `D28_ROOT` at run time.
- Stage-1 models and the full Stage-1 regeneration chain are not shipped (frozen upstream input;
  see the archive repository).

## 3. Generated (not shipped; regenerate)

| path | size | how |
|---|---:|---|
| `rice/outputs/cache/daily_preprocessed_<key>.pkl` | ~5 GB | built on first use from the daily CSV; the key hashes path, mtime and size of the CSV |
| `rice/outputs_allpests_e5d_expB_20260817/…/clean/grid/*.csv` | 21 MB | `scripts/run_b_grid.sh` |
| `audit/selround1_20260818/runs/T/`, `outputs/selector_T_aggregate/` | ~35 MB | `scripts/run_selector_t.sh` |
