# Rice pest occurrence-timing forecast — canonical 8-pest handoff

## 1. Project overview

The system forecasts **when** a rice pest or disease will occur, per **(site, year)**, from daily
weather and past occurrence records:

- **Inputs:** a daily weather table for all sites (1997–2024) and one occurrence-label table per pest.
- **Stage 1** decides whether and when to raise an alert for a site-year (occurrence gate).
- **Stage 2 + selector** then predicts the interval in which the occurrence will fall.
- **Scope:** 8 pests (section 2), each with its own checkpoints and Stage-1 inputs but the same
  canonical configuration.
- **Headline metric:** `IoU80_overall_tol0` — the overlap (IoU) of the predicted 80 % interval with
  the observed occurrence window, counted as 0 when the forecast would come too late, averaged over
  all alerted site-years. It is reported as a **15-cell macro**: eval years 2022, 2023, 2024 × Stage-2
  seeds 0–4.

> **How to read the numbers:** there is no future-year holdout. For eval year *y* the models train on
> years ≤ *y*−2 and select/calibrate on *y*−1, so the 2022–2024 values are temporally valid but
> selection-aware development estimates, not results on untouched test data
> ([audit/HOLDOUT_LOCK_AMENDMENT1_20260818.md](audit/HOLDOUT_LOCK_AMENDMENT1_20260818.md)).

## 2. Target pests

| slug (code/CLI name) | 한글명 | type | label file under `data/rice/LONG_by_pest/` |
|---|---|---|---|
| `WBPH` | 흰등멸구 | insect pest | `RICE_LONG_흰등멸구.csv` |
| `BPH` | 벼멸구 | insect pest | `RICE_LONG_벼멸구.csv` |
| `rice_stem_borer_1` | 이화명나방 1화기 | insect pest | `RICE_LONG_이화명나방1화기.csv` |
| `rice_stem_borer_2` | 이화명나방 2화기 | insect pest | `RICE_LONG_이화명나방2화기.csv` |
| `sheath_blight` | 잎집무늬마름병 | disease | `RICE_LONG_잎집무늬마름병.csv` |
| `bacterial_blight` | 흰잎마름병 | disease | `RICE_LONG_흰잎마름병.csv` |
| `brown_spot` | 깨씨무늬병 | disease | `RICE_LONG_깨씨무늬병.csv` |
| `blast` | 잎도열병 | disease | `RICE_LONG_잎도열병.csv` |

The slug is the name used by every script and directory. Each slug has a module
`rice/pests/<slug>/` whose `config.py` sets the label file (`PATH_OBS`) and the season window, and
whose `features.py` sets the weather feature columns.

## 3. Model pipeline

```
Daily weather + occurrence labels (per pest)
        │
        ▼
Stage 1: XGBoost occurrence gate — FROZEN, not retrained here
        │  alert day + confidence features per alerted site-year
        ▼
Dispatch features  rice/outputs/stage2/<batch>/<pest>/gate_*_R088_features_per_sy.csv  (release asset)
        │
        ▼
Stage 2 "B" (neural interval model, one checkpoint per eval year × seed)
        │  · recent encoder: the last 28 days up to the issue day t
        │  · history branch: the 62 days before that (t−89 … t−28)
        │  · zero-initialised learned gate that mixes the history branch into the recent encoding
        ▼
Offset grid: predicted interval centre/width for issue offsets 1–75 days after the alert
        │
        ▼
Selector T (selector v2): LightGBM, 5 selector seeds, features official_v1 + mu_position;
        │  picks the issue offset per site-year (12 candidates, 3–60 days) and a year-fold shift
        ▼
Final occurrence interval per site-year  →  IoU80_overall_tol0
```

- **"T" is a selector, not a separate temporal neural model.** It is the treatment arm of selector
  round 1 and only chooses among Stage-2 B predictions.
- **Stage 1 is frozen.** Handoff runs and acceptance use the dispatch that was actually passed to
  Stage 2; the tau recorded in it is authoritative (8 pest-years differ from the Stage-1 selection
  CSV; see [docs/CANONICAL_MULTIPEST_DECISION.md](docs/CANONICAL_MULTIPEST_DECISION.md) §6).
- **Season window:** BPH uses DOY 140–270; the other seven pests use DOY 60–300.

## 4. Quick start / environment

Requirements: Linux, **Python 3.12**, an **NVIDIA GPU** (validated on one RTX 4080, driver 580.173.02).
Validated stack: **torch 2.5.1+cu121 / CUDA 12.1 / cuDNN 90100** (installed from the lock; see
[ENVIRONMENT.md](ENVIRONMENT.md)). Disk: about 15 GB free next to the repo
(venv ~6 GB, preprocessing cache ~5.3 GB, release tars 0.44 GB plus the same again extracted,
raw data 1.8 GB if copied locally).

```bash
git clone https://github.com/gilyoung7/rice-pest-timing-forecasting.git
cd rice-pest-timing-forecasting
python3.12 -m venv .venv                      # must be <repo>/.venv: the launchers call .venv/bin/python
.venv/bin/pip install -r requirements.lock    # normal resolver; pulls torch cu121 from the PyTorch index
.venv/bin/pip check                           # must print "No broken requirements found."
```

## 5. Raw data

Raw data is **not** in git and **not** in the GitHub Release; it is an external dependency
(shared storage). The code expects this layout under the data root:

```
data/
└── rice/
    ├── 1997_2024_RICE_union_all_sites_with_GDD10_since_gs.csv    # daily weather (1.7 GB)
    └── LONG_by_pest/
        ├── RICE_LONG_흰등멸구.csv                                 # one file per pest (section 2)
        ├── RICE_LONG_벼멸구.csv
        └── ...                                                   # 8 files in total
```

- **A.** Put or symlink the data root at `<repo>/data` (default): `ln -s /path/to/shared/ygdata data`
- **B.** Or point `RICE_DATA_ROOT` at it: `export RICE_DATA_ROOT=/path/to/shared/ygdata`

Do not use `RICE_DAILY_CSV` / `RICE_LONG_BY_PEST_DIR` (single-file overrides; canonical training aborts
when they are set). Verify the 9 files against `manifests/multipest/RAW_DATA.sha256`:

```bash
(cd "${RICE_DATA_ROOT:-data}" && sha256sum -c "$OLDPWD/manifests/multipest/RAW_DATA.sha256")
```

## 6. Download release assets

The repository is **private**: you need read access to `gilyoung7/rice-pest-timing-forecasting` and
an authenticated GitHub CLI (`gh auth login`).

Release **v2.0.0-multipest-handoff** has 19 tars:
- 7 pests × 2: `<pest>_core.tar` (B checkpoints + splits, frozen dispatch/climatology, reference grids;
  enough for grid and selector) and `<pest>_retrain.tar` (D28/D90 inputs; needed for G0 and retraining);
- WBPH: the 5 verified tars of v1.0.0-handoff, byte-identical (`b_checkpoints_splits`,
  `d28_frozen_norm_checkpoints`, `d90_train_args_splits`, `stage2_dispatch_climatology`, `reference_grids`).

```bash
ASSETS=../rice-pest-assets                    # anywhere outside the repo
gh release download v2.0.0-multipest-handoff -R gilyoung7/rice-pest-timing-forecasting -D "$ASSETS"
# one pest only (its core + retrain tar):
# gh release download v2.0.0-multipest-handoff -R gilyoung7/rice-pest-timing-forecasting -D "$ASSETS" -p 'blast_*'

# check the tars, then extract them AT THE REPO ROOT (paths inside the tars are repo-relative)
(cd "$ASSETS" && sha256sum -c --ignore-missing "$OLDPWD/manifests/RELEASE_ARCHIVES.sha256" \
                                              "$OLDPWD/manifests/multipest/RELEASE_ARCHIVES.sha256")
for t in "$ASSETS"/*.tar; do tar -xf "$t"; done
sha256sum -c --quiet manifests/multipest/RELEASE_ASSETS_blast.sha256    # per pest; WBPH: manifests/RELEASE_ASSETS.sha256
```

Tar contents and layout: [docs/MULTIPEST_DATA.md](docs/MULTIPEST_DATA.md) (7 pests), [DATA.md](DATA.md) (WBPH).

## 7. Run one pest

From the repo root, with the environment, raw data and that pest's assets in place (GPU needed):

```bash
scripts/run_pest_b_grid.sh blast --check       # G1: regenerates the 15 B grids and checks them bitwise
                                                #     against manifests/multipest/B_GRID_SHA256_blast.txt
scripts/run_pest_selector_t.sh blast --anchor  # G2/G3: selector T on the 15 cells; every cell and the
                                                #     15-cell macro must match audit/multipest/blast/canonical_anchor.json (≤1e-12)
```

Optional input check first (G0): `PYTHONPATH=. .venv/bin/python tools/multipest_g0.py blast`.
For `WBPH` the same two launchers call the original WBPH scripts (`scripts/run_b_grid.sh`,
`scripts/run_selector_t.sh`). The first grid run builds the ~5 GB preprocessing cache in
`rice/outputs/cache/`; one pest takes about 20–40 min on an RTX 4080.

**Re-running.** The launchers never overwrite; they abort if their outputs exist. To re-run a pest,
remove only that pest's generated outputs (never the checkpoints, splits or `reference/`):

```bash
P=blast
rm -f rice/outputs_crosspest_frozen_replication_20260818/B/*/seed*/$P/clean/grid/${P}_E5d_clean_grid_1to75.csv   # grids
rm -r outputs/multipest/$P/selector_T/runs                                                                    # selector runs
# WBPH instead: rm -f rice/outputs_allpests_e5d_expB_20260817/*/seed*/WBPH/clean/grid/WBPH_E5d_clean_grid_1to75.csv
#               rm -r audit/selround1_20260818/runs/T
```

The preprocessing cache and the aggregate directories can stay (the cache is reused; aggregates are rewritten).

## 8. Run the full 8-pest acceptance

`scripts/run_multipest_acceptance.sh OUT_DIR [pest ...]` runs G0 → G1 → G2/G3 per pest; a failing
stage stops only that pest. **Without pest arguments it runs the 7 non-WBPH pests only** — list all
8 explicitly for the full acceptance.

> **IMPORTANT: run it inside a tmux session.** Every stage is wrapped by
> `scripts/tmux_terminal_wrapper.sh`, which signals `tmux wait-for`; outside tmux that signal fails
> and stages are recorded as FAILED even when the computation succeeded.

```bash
tmux new -s multipest_acceptance
# inside the tmux session, at the repo root (needs all 19 tars extracted and a fresh checkout state,
# i.e. no grids/selector runs from earlier runs — see section 7 "Re-running"):
scripts/run_multipest_acceptance.sh outputs/acceptance \
  WBPH sheath_blight bacterial_blight brown_spot rice_stem_borer_1 rice_stem_borer_2 BPH blast
```

It takes about 3 h on one RTX 4080 (2.8 h in the 2026-09-27 acceptance). Verdict: `outputs/acceptance/summary.json` — one entry per
pest with the stage states, `G2_cells_pass`, `G3_macro_delta` and `proposed_status`
(`ACCEPTED_HANDOFF_CANONICAL` or `ACCEPTANCE_FAILED` with `failed_stage`); the script exits 0 only if
every listed pest passed. Per-stage logs: `outputs/acceptance/<pest>/`.

## 9. Outputs

All paths are repo-relative; `<y>` = 2022–2024, `<s>` = 0–4.

| artifact | 7 pests (`<pest>`) | WBPH |
|---|---|---|
| grid (G1) | `rice/outputs_crosspest_frozen_replication_20260818/B/<y>/seed<s>/<pest>/clean/grid/<pest>_E5d_clean_grid_1to75.csv` | `rice/outputs_allpests_e5d_expB_20260817/<y>/seed<s>/WBPH/clean/grid/WBPH_E5d_clean_grid_1to75.csv` |
| selector runs | `outputs/multipest/<pest>/selector_T/runs/T/<y>/seed<s>/<pest>/` (`cell_result.json`, `eval/`, `selector_artifacts_v2/`) | `audit/selround1_20260818/runs/T/<y>/seed<s>/WBPH/` |
| aggregate macro (G2/G3) | `outputs/multipest/<pest>/selector_T_aggregate/{cells.csv,aggregate.json}` | `outputs/selector_T_aggregate/{cells.csv,aggregate.json}` |
| logs | `logs/multipest/<pest>/` | `logs/` (`grid_*.log`, `selector_T_*.log`) |
| acceptance summary | `OUT_DIR/summary.json`, `OUT_DIR/<pest>/` | same |

## 10. Reproduced canonical results

Canonical configuration B + selector T, `IoU80_overall_tol0`, 15-cell macro:

| pest | canonical macro | status |
|---|---:|---|
| WBPH | 0.5437853333333333 | ACCEPTED_HANDOFF_CANONICAL (canonical since 2026-08-18) |
| sheath_blight | 0.5841413333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |
| bacterial_blight | 0.4770853333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |
| brown_spot | 0.4953613333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |
| rice_stem_borer_1 | 0.350724 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |
| rice_stem_borer_2 | 0.36444 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |
| BPH | 0.37666266666666665 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27); DOY 140–270 |
| blast | 0.5420426666666667 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) |

Fresh clean-repo acceptance (2026-09-27): **G0 8/8, G1 120/120 grids bitwise, G2 120/120 cells,
G3 8/8 — PASS** (macro delta 0.0 for every pest; record `audit/multipest/ACCEPTANCE_20260927.json`).
The seven non-WBPH pests come from a preregistered frozen replication and were adopted as canonical
at handoff time (`audit/CANONICAL_MULTIPEST.json`).

These values are per-pest reproduction targets, not a ranking: pests differ in data volume, occurrence
patterns, Stage-1 gate and, for BPH, season window (DOY 140–270 vs 60–300), so cross-pest differences should not be
read as research conclusions.

## 11. Where to read next

| document | read it for |
|---|---|
| [HANDOFF.md](HANDOFF.md) | day-to-day operation: pipeline details, common tasks, retraining WBPH, reproducibility limits, project rules |
| [DATA.md](DATA.md) · [docs/MULTIPEST_DATA.md](docs/MULTIPEST_DATA.md) | raw data and release-asset layout (WBPH · the other 7 pests) |
| [ENVIRONMENT.md](ENVIRONMENT.md) | the validated environment and why the lock differs from the original research venv |
| [PROVENANCE.md](PROVENANCE.md) | where every file, checkpoint and number comes from; verification and acceptance history |
| [docs/CANONICAL_MULTIPEST_DECISION.md](docs/CANONICAL_MULTIPEST_DECISION.md) | why the 7 pests are canonical; Stage-1 tau mismatch; BPH caveat; excluded experiments |
| [docs/EXPERIMENT_SUMMARY.md](docs/EXPERIMENT_SUMMARY.md) · [docs/KNOWN_INVALID_RESULTS.md](docs/KNOWN_INVALID_RESULTS.md) | research history; results that must not be cited |
