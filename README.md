# Rice pest occurrence-timing forecast — canonical 8-pest handoff

Minimal, verified code to reproduce the canonical results of the two-stage rice pest
occurrence-timing forecaster for **eight pests**:
WBPH, sheath_blight, bacterial_blight, brown_spot, rice_stem_borer_1, rice_stem_borer_2, BPH, blast.

**Canonical = Stage-1 frozen dispatch → Stage-2 model "B" → selector "T" (selector v2)**, per pest.
Headline `IoU80_overall_tol0`, 15-cell macro (eval years 2022–2024 × Stage-2 seeds 0–4):

| pest | canonical T macro | status | source |
|---|---:|---|---|
| WBPH | 0.5437853333333333 | ACCEPTED_HANDOFF_CANONICAL (canonical since 2026-08-18) | `audit/CANONICAL.json` |
| sheath_blight | 0.5841413333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |
| bacterial_blight | 0.4770853333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |
| brown_spot | 0.4953613333333333 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |
| rice_stem_borer_1 | 0.350724 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |
| rice_stem_borer_2 | 0.36444 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |
| BPH | 0.37666266666666665 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) — DOY 140–270, not directly comparable | crosspest frozen replication |
| blast | 0.5420426666666667 | ACCEPTED_HANDOFF_CANONICAL (2026-09-27) | crosspest frozen replication |

Status and governance: `audit/CANONICAL_MULTIPEST.json`, [docs/CANONICAL_MULTIPEST_DECISION.md](docs/CANONICAL_MULTIPEST_DECISION.md)
(the seven non-WBPH pests were explicitly adopted at handoff time; Stage 1 is not retrained; 8 pest-years
carry a historical Stage-1 tau metadata mismatch).

Verified: fresh clean-repo acceptance on 2026-09-27 — all 8 pests G0–G3 PASS, 120/120 grids
bitwise identical, every selector-T cell within 1e-12 of its anchor, macro delta 0.0 for all pests
(see [PROVENANCE.md](PROVENANCE.md) §4).

## Quick start (reproduce the headline numbers)

```bash
# 1. environment (see ENVIRONMENT.md)
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.lock

# 2. raw data (see DATA.md): make data/ point at the shared data root (daily table + 8 label files)
ln -s /path/to/shared/ygdata data
(cd data && sha256sum -c "$OLDPWD/manifests/multipest/RAW_DATA.sha256")

# 3. release assets (GitHub Release v2.0.0-multipest-handoff): 5 WBPH tars + 2 tars per other pest
for t in /path/to/assets/*.tar; do tar -xf "$t"; done
sha256sum -c manifests/RELEASE_ASSETS.sha256                               # WBPH
for p in sheath_blight bacterial_blight brown_spot rice_stem_borer_1 rice_stem_borer_2 BPH blast; do
  sha256sum -c --quiet "manifests/multipest/RELEASE_ASSETS_$p.sha256"; done

# 4. per pest: regenerate the 15 B grids (G1), then selector T + anchor gate (G2/G3)
scripts/run_pest_b_grid.sh blast --check          # WBPH: delegates to scripts/run_b_grid.sh
scripts/run_pest_selector_t.sh blast --anchor     # WBPH: delegates to scripts/run_selector_t.sh

# or all gates for several pests (inside tmux): G0 -> G1 -> G2/G3 per pest
scripts/run_multipest_acceptance.sh /tmp/acceptance sheath_blight BPH
```

GPU required for step 4 (grid forward). The first grid run builds a ~5 GB preprocessing cache
under `rice/outputs/cache/` (regenerable, not shipped). Runtime on one RTX 4080: ~20–40 min per pest.

## Layout

| path | content |
|---|---|
| `rice/` | pipeline code, original module layout kept (`rice.src`, `rice.scripts`, `rice.configs`, `rice.pests.<pest>` for all 8 pests) |
| `rice/experiments/allpests_e5d/` | Stage-2 E5d driver: `pest_grid.py`, `pest_eval.py`, `vendor/` (model + trainer) |
| `audit/selround1_20260818/run_selector_cell.py` | unchanged WBPH per-cell selector runner (path kept: it resolves the repo root from its location) |
| `scripts/` | WBPH: `run_b_grid.sh`, `run_selector_t.sh`, `run_expb_cell.sh` (retraining); all pests: `run_pest_b_grid.sh`, `run_pest_selector_t.sh`, `run_multipest_acceptance.sh`; `tmux_terminal_wrapper.sh` |
| `tools/` | `aggregate_selector_cells.py` (WBPH); `pest_grid_reroot.py`, `run_pest_selector_cell.py`, `aggregate_pest_cells.py`, `multipest_g0.py` (other pests) |
| `audit/` | WBPH decision records (verbatim), `canonical_anchor.json`; `CANONICAL_MULTIPEST.json`; `multipest/<pest>/canonical_anchor.json`; `multipest/ACCEPTANCE_20260927.json`; verbatim crosspest records |
| `manifests/` | code provenance, release-asset and data sha256 lists (`manifests/multipest/` for the other pests) |
| `docs/` | multi-pest decision and assets, experiment summary, known invalid results, research direction |

## Read next

[HANDOFF.md](HANDOFF.md) (pipeline and how to work with it) · [DATA.md](DATA.md) ·
[docs/MULTIPEST_DATA.md](docs/MULTIPEST_DATA.md) · [ENVIRONMENT.md](ENVIRONMENT.md) ·
[PROVENANCE.md](PROVENANCE.md) · [docs/CANONICAL_MULTIPEST_DECISION.md](docs/CANONICAL_MULTIPEST_DECISION.md) ·
[docs/EXPERIMENT_SUMMARY.md](docs/EXPERIMENT_SUMMARY.md) · [docs/KNOWN_INVALID_RESULTS.md](docs/KNOWN_INVALID_RESULTS.md)
