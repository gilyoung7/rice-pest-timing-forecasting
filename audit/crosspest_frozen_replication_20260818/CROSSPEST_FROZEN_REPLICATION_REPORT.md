# Cross-pest frozen replication aggregation

## Scope and preregistration

Source preregistration: `rice/outputs_crosspest_frozen_replication_20260818/audit/CROSSPEST_FROZEN_PREREG.md`  
SHA256: `426411b5fb5662e435e7da078b54073c9f5ac6b35d2af5aa0ee0b1d7346e71da`

This is a read-only arithmetic aggregation of persisted official per-cell
`clean_pooled_metrics.csv` files and persisted candidate/pick artifacts. No
training, inference, selector fitting, or evaluation was run. The headline is
the preregistered `IoU80_overall_tol0`, macro-averaged across the 15
year×Stage-2-seed cells. Lead-bin values apply the canonical late mask to
persisted selected candidate rows, average selector seeds within sample, then
sample-average within cell and macro-average across cells. Binning is the
official `L - alert_tstar`: <=60, 61-75, >75.

The reproduction/recovery class labels below are **exploratory descriptive
labels**, because the preregistration fixes the replication but does not define
these four category thresholds. `reproduced` means D90: short<0, both long bins
>0; B: short>0 and both long bins>=0. `partial` means the short direction and
at least one required long-bin direction hold. `opposite` requires all three
directions reversed; all other cases are `not_reproduced`.

## 15-cell headline macro and paired deltas

| pest | D28 | D90 | B | selector | D90_minus_D28 | B_minus_D90 |
|---|---|---|---|---|---|---|
| brown_spot | 0.299161 | 0.314957 | 0.439151 | 0.495361 | 0.015796 | 0.124193 |
| rice_stem_borer_2 | 0.244912 | 0.280379 | 0.324527 | 0.364440 | 0.035467 | 0.044148 |
| rice_stem_borer_1 | 0.239872 | 0.269971 | 0.329131 | 0.350724 | 0.030099 | 0.059160 |
| sheath_blight | 0.378360 | 0.316955 | 0.442897 | 0.584141 | -0.061405 | 0.125943 |
| blast | 0.395680 | 0.353268 | 0.405969 | 0.542043 | -0.042412 | 0.052701 |
| BPH | 0.268532 | 0.297883 | 0.318723 | 0.376663 | 0.029351 | 0.020840 |
| bacterial_blight | 0.338441 | 0.368645 | 0.422101 | 0.477085 | 0.030204 | 0.053456 |

## 15-cell dispersion (sample SD across 15 year×seed cell metrics)

| pest | D28 | D90 | B | selector |
|---|---|---|---|---|
| brown_spot | 0.044180 | 0.066507 | 0.042399 | 0.039105 |
| rice_stem_borer_2 | 0.135902 | 0.167023 | 0.201238 | 0.212400 |
| rice_stem_borer_1 | 0.056210 | 0.097214 | 0.102497 | 0.102732 |
| sheath_blight | 0.032133 | 0.073886 | 0.101055 | 0.063646 |
| blast | 0.037490 | 0.060762 | 0.080855 | 0.075688 |
| BPH | 0.077097 | 0.116231 | 0.094820 | 0.111580 |
| bacterial_blight | 0.022233 | 0.066724 | 0.073199 | 0.094407 |

## Dispersion direction

| pest | D28 | D90 | B | D90_minus_D28 | B_minus_D90 | D90_variance_change | B_vs_D90 |
|---|---|---|---|---|---|---|---|
| brown_spot | 0.044180 | 0.066507 | 0.042399 | 0.022327 | -0.024108 | increased | mitigated |
| rice_stem_borer_2 | 0.135902 | 0.167023 | 0.201238 | 0.031121 | 0.034216 | increased | not_mitigated |
| rice_stem_borer_1 | 0.056210 | 0.097214 | 0.102497 | 0.041004 | 0.005283 | increased | not_mitigated |
| sheath_blight | 0.032133 | 0.073886 | 0.101055 | 0.041752 | 0.027169 | increased | not_mitigated |
| blast | 0.037490 | 0.060762 | 0.080855 | 0.023273 | 0.020093 | increased | not_mitigated |
| BPH | 0.077097 | 0.116231 | 0.094820 | 0.039135 | -0.021412 | increased | mitigated |
| bacterial_blight | 0.022233 | 0.066724 | 0.073199 | 0.044492 | 0.006475 | increased | not_mitigated |

## Official lead-bin macro and paired deltas

| pest | lead_bin | D28 | D90 | B | selector | D90_minus_D28 | B_minus_D90 |
|---|---|---|---|---|---|---|---|
| BPH | 61-75 | 0.114593 | 0.226192 | 0.264020 | 0.370326 | 0.111599 | 0.037828 |
| BPH | <=60 | 0.318390 | 0.331265 | 0.356387 | 0.400017 | 0.012875 | 0.025122 |
| BPH | >75 | 0.127381 | 0.135652 | 0.204997 | 0.297601 | 0.008271 | 0.069345 |
| bacterial_blight | 61-75 | 0.292222 | 0.381015 | 0.491732 | 0.499868 | 0.088793 | 0.110717 |
| bacterial_blight | <=60 | 0.413354 | 0.407987 | 0.421585 | 0.501306 | -0.005367 | 0.013597 |
| bacterial_blight | >75 | 0.067831 | 0.224403 | 0.318931 | 0.379127 | 0.156572 | 0.094528 |
| blast | 61-75 | 0.177257 | 0.246887 | 0.444012 | 0.484483 | 0.069630 | 0.197125 |
| blast | <=60 | 0.499704 | 0.397152 | 0.404937 | 0.586597 | -0.102553 | 0.007785 |
| blast | >75 | 0.003789 | 0.193750 | 0.370607 | 0.343575 | 0.189962 | 0.176857 |
| brown_spot | 61-75 | 0.378177 | 0.351568 | 0.488885 | 0.538150 | -0.026609 | 0.137317 |
| brown_spot | <=60 | 0.317838 | 0.346576 | 0.418766 | 0.508154 | 0.028738 | 0.072190 |
| brown_spot | >75 | 0.172136 | 0.185303 | 0.490473 | 0.417502 | 0.013167 | 0.305170 |
| rice_stem_borer_1 | 61-75 | 0.132817 | 0.326864 | 0.360253 | 0.395896 | 0.194047 | 0.033390 |
| rice_stem_borer_1 | <=60 | 0.398120 | 0.353475 | 0.405221 | 0.431006 | -0.044645 | 0.051746 |
| rice_stem_borer_1 | >75 | 0.011642 | 0.123012 | 0.205790 | 0.261607 | 0.111370 | 0.082778 |
| rice_stem_borer_2 | 61-75 | 0.221267 | 0.391013 | 0.451444 | 0.490768 | 0.169746 | 0.060432 |
| rice_stem_borer_2 | <=60 | 0.299816 | 0.302182 | 0.329519 | 0.377568 | 0.002365 | 0.027337 |
| rice_stem_borer_2 | >75 | 0.114201 | 0.211051 | 0.371091 | 0.331433 | 0.096850 | 0.160040 |
| sheath_blight | 61-75 | 0.307679 | 0.323081 | 0.474057 | 0.572940 | 0.015402 | 0.150976 |
| sheath_blight | <=60 | 0.494154 | 0.345806 | 0.436505 | 0.625311 | -0.148348 | 0.090699 |
| sheath_blight | >75 | 0.073666 | 0.235571 | 0.417476 | 0.439397 | 0.161905 | 0.181905 |

Lead-bin cell coverage is stored in `CROSSPEST_FROZEN_CELL_VALUES.csv`.
For BPH, the 61-75 bin has 10/15 non-empty cells and >75 has 5/15; for
rice_stem_borer_1, 61-75 has 10/15; for rice_stem_borer_2, 61-75 and >75 each
have 10/15. All other pest×bin combinations have 15/15 non-empty cells.

## Replication classification (exploratory)

| pest | D90_reversal_class | B_recovery_class | D90_short_delta | D90_61_75_delta | D90_gt75_delta | B_short_delta | B_61_75_delta | B_gt75_delta |
|---|---|---|---|---|---|---|---|---|
| brown_spot | not_reproduced | reproduced | 0.028738 | -0.026609 | 0.013167 | 0.072190 | 0.137317 | 0.305170 |
| rice_stem_borer_2 | not_reproduced | reproduced | 0.002365 | 0.169746 | 0.096850 | 0.027337 | 0.060432 | 0.160040 |
| rice_stem_borer_1 | reproduced | reproduced | -0.044645 | 0.194047 | 0.111370 | 0.051746 | 0.033390 | 0.082778 |
| sheath_blight | reproduced | reproduced | -0.148348 | 0.015402 | 0.161905 | 0.090699 | 0.150976 | 0.181905 |
| blast | reproduced | reproduced | -0.102553 | 0.069630 | 0.189962 | 0.007785 | 0.197125 | 0.176857 |
| BPH | not_reproduced | reproduced | 0.012875 | 0.111599 | 0.008271 | 0.025122 | 0.037828 | 0.069345 |
| bacterial_blight | reproduced | reproduced | -0.005367 | 0.088793 | 0.156572 | 0.013597 | 0.110717 | 0.094528 |

Counts: D90 reversal classes = `{"not_reproduced": 3, "reproduced": 4}`; B
recovery classes = `{"reproduced": 7}`.

## Artifact checks

All 7 pests have 15/15 persisted metric CSVs for each D28, D90, B, and selector
arm. Candidate-to-pick joins were one-to-one for each selector-seed pick row;
the per-cell candidate-derived headline values are used only for lead-bin
decomposition and may differ from five-decimal persisted headline CSV values
by rounding.
