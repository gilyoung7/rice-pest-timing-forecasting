# Multi-pest handoff canonical decision

Decision date: 2026-09-27. Machine-readable status: `audit/CANONICAL_MULTIPEST.json`.
This document adds a decision; it does not amend any earlier record. `audit/CANONICAL.json`,
the verdicts, the preregistrations and the crosspest report stay as they are.

## 1. Decision

For the handoff, the Stage-2 **B + selector T (selector v2 = official_v1 + mu_position)**
produced by the cross-pest frozen replication (`rice/outputs_crosspest_frozen_replication_20260818`,
arms `B` and `selector`) is adopted as the canonical configuration for seven pests:
sheath_blight, bacterial_blight, brown_spot, rice_stem_borer_1, rice_stem_borer_2, BPH, blast.

Only the `selector` arm (T) is adopted. The crosspest `D28`, `D90` and `B` (selector v1) arms
are not canonical; D28 checkpoints and D90 arguments/splits are kept only as B retraining inputs.

| pest | status | frozen T macro (`IoU80_overall_tol0`, 15 cells) | anchor |
|---|---|---:|---|
| WBPH | ACCEPTED_HANDOFF_CANONICAL (unchanged, canonical since 2026-08-18) | 0.5437853333333333 | `audit/canonical_anchor.json` |
| sheath_blight | ADOPTED_PENDING_ACCEPTANCE | 0.5841413333333333 | `audit/multipest/sheath_blight/canonical_anchor.json` |
| bacterial_blight | ADOPTED_PENDING_ACCEPTANCE | 0.4770853333333333 | `audit/multipest/bacterial_blight/canonical_anchor.json` |
| brown_spot | ADOPTED_PENDING_ACCEPTANCE | 0.4953613333333333 | `audit/multipest/brown_spot/canonical_anchor.json` |
| rice_stem_borer_1 | ADOPTED_PENDING_ACCEPTANCE | 0.350724 | `audit/multipest/rice_stem_borer_1/canonical_anchor.json` |
| rice_stem_borer_2 | ADOPTED_PENDING_ACCEPTANCE | 0.36444 | `audit/multipest/rice_stem_borer_2/canonical_anchor.json` |
| BPH | ADOPTED_PENDING_ACCEPTANCE | 0.37666266666666665 | `audit/multipest/BPH/canonical_anchor.json` |
| blast | ADOPTED_PENDING_ACCEPTANCE | 0.5420426666666667 | `audit/multipest/blast/canonical_anchor.json` |

Macros are `math.fsum` of the 15 cell values / 15 (same rule as `tools/aggregate_selector_cells.py`);
they agree with `CROSSPEST_FROZEN_MACRO.csv` within 1e-12.

## 2. Status vocabulary

| status | meaning |
|---|---|
| `ADOPTED_PENDING_ACCEPTANCE` | adopted by this decision; clean-repo acceptance (G0–G3) not yet run |
| `ACCEPTED_HANDOFF_CANONICAL` | adopted and G0–G3 passed in a fresh clean clone |
| `ACCEPTANCE_FAILED` | adopted, but a gate failed; recorded explicitly with the failing gate and never silently removed from the handoff or release notes |

Gates (per pest, independent): G0 input sha256 (dispatch, climatology, labels, assets, D28 ↔
`frozen_norm_source.sha256`); G1 15/15 grids bitwise vs `manifests/multipest/B_GRID_SHA256_<pest>.txt`;
G2 15/15 selector-T cells within 1e-12 of the anchor; G3 macro within 1e-12.
Every status change is a new `history` entry in `audit/CANONICAL_MULTIPEST.json` with its acceptance record.

## 3. Why the seven replications are adopted

- They ran the finalized WBPH protocol unchanged (prereg `CROSSPEST_FROZEN_PREREG.md`,
  sha256 `426411b5fb5662e435e7da078b54073c9f5ac6b35d2af5aa0ee0b1d7346e71da`): same architecture,
  loss, lead range, candidate offsets, selector features and y−1 fitting; no configuration was tuned on outcomes.
- All 7 × 15 cells completed with persisted checkpoints, grids and selector outputs
  (run COMPLETED, exit 0, 2026-08-18); no invalidity marker exists for this output directory.
- The handoff needs one operable, documented configuration per pest. The frozen-protocol result is
  the only full 15-cell B + T lineage available for these pests.

## 4. Relation to the preregistration

The crosspest preregistration states that outcomes "are not grounds for retrospective tuning or
automatic canonical promotion". That clause is not overridden and is not contradicted:

- This is not an automatic promotion triggered by the results. It is a separate governance decision
  taken at handoff time for operational scope, recorded here after the fact.
- Nothing was retuned; the adopted artifacts are exactly the preregistered frozen outputs.
- The scientific framing is unchanged: the seven pests remain within-domain replication evidence,
  not multi-domain evidence (see `docs/RESEARCH_DIRECTION_CORE.md`).

WBPH was canonical during the research (`audit/SELROUND1_VERDICT_20260818.md`); the seven other pests
become canonical only through this handoff decision.

## 5. Stage 1 policy

Stage 1 is not retrained or regenerated. For every pest (WBPH included) the per-(site, year)
dispatch CSV that was actually passed to Stage 2 is the authoritative Stage-1 input:
`rice/outputs/stage2/<batch>/<pest>/gate_<method>_R088_features_per_sy.csv`
(sha256 in `manifests/multipest/STAGE1_DISPATCH.sha256`; WBPH in `manifests/RELEASE_ASSETS.sha256`).
Stage-1 models and the regeneration chain stay in the archive.

## 6. Tau record mismatch

The authoritative operating point is the tau actually used to build the dispatch
(`dispatch_tau_used` column of the dispatch CSV), not the value in the Stage-1 selection CSV
(`rice/outputs/stage2/<batch>/_summary/stage1_gate_selection_split*_<year>.csv`).
All 24 pest × year rows are listed in `manifests/multipest/STAGE1_OPERATING_POINTS.csv`.
The gate method agrees in 24/24 rows; tau agrees in 16/24. The 8 rows below are
`HISTORICAL_METADATA_MISMATCH`:

| pest | year | method | selection-CSV tau | dispatch tau used |
|---|---|---|---:|---:|
| bacterial_blight | 2022 | A_baseline | 0.45 | 0.425 |
| brown_spot | 2022 | A_baseline | 0.525 | 0.50 |
| rice_stem_borer_1 | 2022 | A_baseline | 0.675 | 0.625 |
| blast | 2022 | A_baseline | 0.60 | 0.575 |
| bacterial_blight | 2023 | D_history | 0.55 | 0.525 |
| brown_spot | 2023 | D_history | 0.525 | 0.50 |
| bacterial_blight | 2024 | D_history | 0.575 | 0.525 |
| rice_stem_borer_1 | 2024 | A_baseline | 0.575 | 0.55 |

WBPH has no mismatch. The selection CSVs are not edited. Stage-2 results remain valid because they
were computed from the actual dispatch. The cause of the mismatch is not established from the files,
and the Stage-1 `selected_run` cannot be verified from the dispatch CSV.
(The planning note of 2026-09-27 stated "9 cells"; the verified count is 8.)

## 7. BPH geometry caveat

BPH keeps its historical season window DOY 140–270 (T = 131; `rice/pests/BPH/config.py`), while the
other seven pests use DOY 60–300 (T = 241). BPH numbers are not claimed to be directly comparable
with the other pests. Retraining BPH on DOY 60–300 is outside this handoff.

## 8. Not canonical

Weather augmentation; no-occurrence-history; warm-start / multipest pretrain; gate regularization;
early-context / pre60; temporal importance; mechanism battery / PH; RSB1 winter; sheath_blight
do-no-harm; arch calibration; all other ablations and diagnostics; crosspest D28, D90 and B
(selector v1) arms. Results listed in `docs/KNOWN_INVALID_RESULTS.md` stay invalid.

## 9. Other recorded caveats

- No run-time grid sha256 was recorded for the crosspest run. The expected grid hashes were derived
  on 2026-09-27 from the persisted 2026-08-18 grids; each equals its independent selector-arm copy (105/105).
- The crosspest output directory is not in any git commit. The six decision-relevant records are
  copied verbatim to `audit/crosspest_frozen_replication_20260818/`; the full directory is to be
  preserved as a separate provenance asset in the private archive repository.
- The executed `pest_eval.py` (archive `7029760`) differs from the handoff blob (`fec1409`) only by a
  W&B entity import/default; equivalence is established by G2, not assumed.
- Crosspest trained every pest with `--batch_train_override 16`; the `b16_cells` column of
  `rice/experiments/allpests_e5d/pests.tsv` describes the earlier production runs, not this lineage.

## 10. Provenance references

| item | reference |
|---|---|
| crosspest outputs | `/home/gpu4080/research/cropscience_multipest/rice/outputs_crosspest_frozen_replication_20260818` (local, not in git) |
| crosspest drivers | archive commit `7029760` (first commit of the executed blobs; sha256 match `inputs_manifest.txt`), also in snapshot `83dc4a3` |
| training code | `fec1409` (`canonical-B-train`); checkpoint `code_provenance` 105/105 |
| file-level provenance | `manifests/multipest/CODE_MANIFEST.csv`, `manifests/multipest/PROVENANCE_MULTIPEST.csv` |
| WBPH record | `audit/CANONICAL.json`, PROVENANCE.md §4 (acceptance r3 on `91da3f7`) |
