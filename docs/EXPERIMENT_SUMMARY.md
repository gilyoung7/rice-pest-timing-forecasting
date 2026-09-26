# Experiment summary (outside the canonical pipeline)

These results are summaries only. Their code and outputs are **not** in this repository; the
"archive source" column gives the path in the archive repository (PROVENANCE.md §1). Most
September code lives only on the archive branch `snapshot/sept-experiment-hooks`, and several
depend on uncommitted hook flags in the canonical training files, which this repository does not
carry (it uses the verified `fec1409` code). Numbers are `IoU80_overall_tol0` means unless noted.
All are development-period estimates (no future-year holdout).

## 1. Context extension: D28 → D90 → B → T (WBPH, 15 cells)

| step | macro | Δ | archive source |
|---|---:|---:|---|
| D28 | 0.3233 | — | `audit/d28_frozen_manifest.txt` |
| D90 | 0.3789 | +0.0556 vs D28 | `audit/D90_CANONICAL_DECISION.md` |
| B (selector v1) | 0.4497 | +0.0707 vs D90 | `audit/EXPB_VERDICT_20260817.md` |
| B + T | 0.5438 | +0.0941 vs B+v1 | `audit/SELROUND1_VERDICT_20260818.md` |

D90 helped long leads but hurt short leads (lead-bin deltas vs D28: ≤60 −0.059, 61–75 +0.136,
>75 +0.219); B recovered short leads (≤60 +0.069 vs D90) and kept long-lead gains
(`docs/RESEARCH_DIRECTION_CORE.md`). Early-stopping truncation was audited and rejected
(`audit/earlystop_audit_20260815/`).

## 2. Cross-pest frozen replication (7 more pests)

Same frozen D28 → D90 → B → T protocol, newly trained per pest.
B beat D90 in 7/7 pests; T beat B in 7/7; D90 mean reversal reproduced in 4/7; B reduced seed
variance in only 2/7. Pooled: D90−D28 +0.005, B−D90 +0.069, T over B +0.073.
Archive: `rice/outputs_crosspest_frozen_replication_20260818/audit/CROSSPEST_FROZEN_REPLICATION_REPORT.md`.

Selector C vs T per pest (corrected table; the original concatenated table is invalid):

| pest | C | T | T−C |
|---|---:|---:|---:|
| WBPH | 0.4497 | 0.5438 | +0.0941 |
| BPH | 0.3187 | 0.3767 | +0.0579 |
| bacterial_blight | 0.4221 | 0.4771 | +0.0550 |
| blast | 0.4060 | 0.5420 | +0.1361 |
| brown_spot | 0.4392 | 0.4954 | +0.0562 |
| rice_stem_borer_1 | 0.3291 | 0.3507 | +0.0216 |
| rice_stem_borer_2 | 0.3245 | 0.3644 | +0.0399 |
| sheath_blight | 0.4429 | 0.5841 | +0.1412 |

Archive: `audit/selround1_20260818/crosspest_ct_calibration_20260821/corrected_local/ct_8pest_absolute_iou80_corrected.csv`.

## 3. Occurrence-history removal (corrected, 8 pests × 3 years × 5 seeds = 120 cells)

Removing occurrence-history inputs (neighbour history + Stage-1 history-derived dispatch/selector
features) from B + T: overall Δ = **+0.0042** (62 wins / 58 losses) — essentially neutral, but
pest-dependent:

| pest | canonical | no-history | Δ |
|---|---:|---:|---:|
| BPH | 0.3767 | 0.4375 | +0.0608 |
| WBPH | 0.5438 | 0.5300 | −0.0138 |
| bacterial_blight | 0.4771 | 0.4899 | +0.0128 |
| blast | 0.5420 | 0.5623 | +0.0203 |
| brown_spot | 0.4954 | 0.5213 | +0.0260 |
| rice_stem_borer_1 | 0.3507 | 0.3027 | −0.0480 |
| rice_stem_borer_2 | 0.3644 | 0.3218 | −0.0427 |
| sheath_blight | 0.5841 | 0.6021 | +0.0179 |

Archive: `rice/outputs_no_occurrence_history_corrected/analysis_corrected_120_20260909/corrected_nohistory_120cell_report.md`
(run root `…/expB_improvedT_3year_20260908_r3`). The first no-history run is invalid
(KNOWN_INVALID_RESULTS.md).

## 4. Weather augmentation (temperature perturbation)

**WBPH (no-history base).** Arms A0 (none), J1 (α 0.02), J2 (α 0.05), p = 0.5; J1 frozen on
validation (0.5873 vs A0 0.5669) before test. 2024 test: J1 0.5789 vs A0 0.5480 (Δ +0.031, 4/5 B
seeds positive). Archive: `rice/outputs_wbph_weather_augmentation_20260911/` (`frozen_selection.json`,
`final_2024_test_paired_metrics.csv`, `completion_summary.json`).

**Fixed J1, six other pests** (BPH schema-blocked). 2024 held-out: pest-level macro ΔFinal
+0.0013 (median −0.0001); 3 pests up, 3 down. Blast positive (95% CI [0.012, 0.030]),
sheath_blight negative (CI [−0.023, −0.0002]); others' CIs include 0. Conclusion: pest-dependent,
no general gain. Archive: `rice/outputs_multipest_fixed_j1_augmentation_20260914/FINAL_REPORT.md`
(the "full" stage failed on a controller assertion and was completed by a recorded recovery).

## 5. WBPH temporal importance (block occlusion, corrected)

Occlusion of relative-lag blocks with full-cohort frozen-T replay. Physical-site-year cluster
bootstrap (10,000 replicates) effects are small (all |mean| ≤ 0.0011); recent lags (0–27 days,
`recent_28`) show small positive values with CIs above 0; the 49–83-day blocks are small negative
with CIs below 0; `history_62` and the 28–48 and 84–89-day blocks have CIs that include 0. See the source for the exact metric definition.
Archive: `audit/wbph_temporal_importance_20260910/` — use only the files marked VALID in its
`INVALID.md` (`cluster_bootstrap.csv`, `relative_block_candidate_diagnostics_v2.*`,
`frozenT_end_to_end.csv`, corrected absolute-DOY / early-context files).

## 6. WBPH history-gate regularisation

λ ∈ {0, 1e-4, 1e-3, 1e-2} on the no-history WBPH base. Validation best was λ=1e-3 (0.5683) but
λ=0 (0.5669) is within the frozen 0.002 margin, so the rule selects λ=0 → test identical to
baseline. **Null result.** Archive: `rice/outputs_wbph_history_gate_regularization_20260911/recovery/REPORT.md`.

## 7. Mechanism battery B0–B5 (frozen conclusions)

Source: `audit/mechanism_battery_20260818/BATTERY_VERDICT.md` (2026-09-03).

| decision | outcome |
|---|---|
| D1 (B1 probes) | encoder-level representation-damage claim discarded |
| D2 (B2 balanced loss) | H2 promotion unmet for all pests; WBPH discard condition met |
| D3 (B3 matched capacity) | parameter-count-only account weakened |
| D4 (B4 head/readout, sampling) | WBPH unresolved; sheath_blight supports head-local objective/sampling sensitivity |
| D5 / D6 (B0) | pest-heterogeneous exploratory records |
| D7 (B5 gradient conflict, final checkpoint) | unresolved (WBPH, sheath_blight); trajectory analysis closed-infeasible |

The full mechanism of B's gain remains unresolved. The post-hoc PH functional decomposition
(`PH_FUNCTIONAL_DECOMPOSITION_RESULTS_20260903.md`, canonical run `ph_functional_decomposition_canonical_20260904/`)
is exploratory and outside the battery.

## 8. Other experiments (archive only)

Encoder ablation (encoder needed), arms E/F and asym×lead_max 2×2 (all below D28), multi-pest
pretraining/warm-start, curriculum, RSB1/sheath_blight previous-winter adapters and branch×offset
selectors (negative or small; "RSB1 search closed"), early-context DOY1 and pre-60 weighting
(below canonical). See the archive `audit/` and `rice/outputs_*` directories.
