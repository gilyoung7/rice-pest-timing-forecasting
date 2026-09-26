# Known invalid or superseded results

None of these files are in this repository. They remain in the archive repository, where each
location carries an `INVALID.md` marker (added 2026-09-26; committed on branch
`snapshot/sept-experiment-hooks`) with file-level INVALID / SUPERSEDED / VALID-replacement
entries. Do not cite the invalid items.

| archive location | status | reason | valid replacement |
|---|---|---|---|
| `audit/wbph_temporal_importance_20260910/relative_block_candidate_diagnostics.{csv,parquet}` | INVALID | first run used an incomplete cohort (989 vs 1248 rows per cell; right-censored candidates dropped) and no frozen-T replay | `relative_block_candidate_diagnostics_v2.*`, `frozenT_end_to_end.csv` |
| same dir: `relative_block_summary.csv`, `coarse_recent_history.csv` | INVALID | derived from the invalid first-run diagnostics; no v2 exists | `cluster_bootstrap.csv` |
| same dir: `terminal_state.json` (COMPLETED), `recompute_state.json` (RUNNING) | misleading / stale | refer to the invalid first run / an interrupted recompute | `pipeline_status.json`, `final_summary.md` |
| `rice/outputs_no_occurrence_history/` (all run and analysis dirs) | INVALID | "no-history B" checkpoints were plain D90 and selectors lacked `mu_position` (`provenance_audit_20260904/`) | `rice/outputs_no_occurrence_history_corrected/expB_improvedT_3year_20260908_r3` + `analysis_corrected_120_20260909` |
| `rice/outputs_no_occurrence_history_corrected/expB_improvedT_3year_20260908` (r1), `_r2` | SUPERSEDED | preflight / debug only | `_r3` |
| `audit/sample_dump_20260816/`, `audit/sample_dump_v2_20260816/` (+`v3/`), `audit/blend_diag_20260816/` | DEPRECATED | obsolete D28/D90 slot mapping (contaminated pairing) | `audit/sample_dump_v4_20260817/` |
| `audit/results/diagnostic_shift_absorption.csv`, `diagnostic_shift_geometry_residual.csv` | INVALID | shift parser bug (zero-shift fallback) | `*_corrected_v2.csv` |
| `audit/results/*_corrected.csv` (non-v2) | SUPERSEDED | — | `*_corrected_v2.csv` |
| `audit/selround1_20260818/crosspest_ct_calibration_20260821/analysis/{paired_performance,bias_summary}_all_pests.csv` and the C/T tables in the 7 W&B `*_selector_mu_position_calibration` runs | INVALID | cumulative concatenation duplicated pest rows | `corrected_local/ct_8pest_absolute_iou80_corrected.csv` |
| `rice/outputs_stage2_batch_*/_summary`, `_offset_selector_v2*` (legacy lead_v3 era) | INVALID | wrong normalisation (mu shifted ≈ 20 days) | see `_WRONG_NORM_README.md` there |
| `audit/mechanism_battery_20260818/`: `ph_functional_decomposition_run_control`, `ph_functional_decomposition_results_20260903`, `ph_canonical_full_equivalence_preflight_20260903` (+ run control), `ph_implementation_verification` (prefinal), `b3_eval_canonical`, `b5_gradient_conflict_run_control`; `b2_eval` not authoritative | FAILED / SUPERSEDED | see that dir's `INVALID.md` | `*_canonical_20260904`, `*_floatguard_20260904`, `*_final`, `b3_eval_canonical_r2`, `b5_gradient_conflict_canonical`, `b2_eval_canonical` |
| `rice/outputs_wbph_expB_early_context_doy1_20260827` (r1) | INVALID | interrupted at epoch 1, no checkpoint | `_r2` |
| `audit/rsb1_benefit_gate_20260903/STOP_REPORT.md`, `analysis/predictor_metrics.csv` | SUPERSEDED | run resumed; metric column fixed | `analysis/FINAL_REPORT.md`, `predictor_metrics_corrected.csv` |
| `audit/EXPB_VERDICT_20260817.md` §"Initial subset values"; `audit/DIAGNOSTIC_PRE_ARM_SELECTION.md` shift statements; `ENCODER_ABLATION_REPORT.*draft*.md`, `ENCODER_ABLATION_PLAN.json.orig` | SUPERSEDED | non-official binning / parser bug / drafts | corrected sections / final reports |
| `audit/selround1_20260818/finalize_selround1.py`, its `terminal_state.json` (FAILED) | provenance gap (results VALID) | executed finalizer not in git | canonical `cells.csv` equals the 45 `cell_result.json`; this repo uses `tools/aggregate_selector_cells.py` |
