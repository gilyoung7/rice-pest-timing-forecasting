# Cross-pest frozen replication preregistration

Date: 2026-08-18

## Scope

This is a frozen replication of the finalized WBPH progression, not a tuning
exercise. The targets are `brown_spot`, `rice_stem_borer_2`,
`rice_stem_borer_1`, `sheath_blight`, `blast`, `BPH`, and
`bacterial_blight`. WBPH is excluded from training and remains unchanged.

Each pest uses exactly the same Stage-2 configuration: D28 (window 28), D90
(window 90 with its matching new D28 checkpoint as frozen paired-norm source),
and Experiment B (28-day recent branch plus 62-day history branch, d=48,
4 heads, 1 history layer, zero-initialized gate/projection). All use seeds
0--4 and test years 2022--2024, with `train <= y-2`, validation `y-1`, and
test `y`.

The fixed common protocol is: d_model=48, n_head=4, n_layers=3,
split_seed=42, scratch initialization, Gaussian sigma=5,
`stage2_pmf_asym_weight=5`, `stage2_pmf_asym_weight_early=0`, lead range
7--140, `require_tstar_before_L=1`, the WBPH optimizer/schedule/epoch and
checkpoint-selection protocol, E5d clean evaluation, the fixed candidate
offset set `{3,7,14,21,28,30,35,42,45,49,56,60}`, and five-selector-seed
y-1 fitting/calibration. The final selector treatment is exactly
`official_v1 + mu_position`; no other selector feature is permitted.

No result from one pest may alter any configuration for another. Intermediate
performance cannot alter a hyperparameter, loss, architecture, candidate
offset, initialization, cohort, normalization, or selector. Legacy
checkpoints are never substituted for the new D28/D90/B lineage. The 2026
and final temporal holdouts remain unopened.

## Execution and gates

For every pest, the first lineage is 2022/seed0:

`D28 -> D90 (paired D28 norm) -> B -> selector-v1 -> mu_position selector`.

It must pass model construction, scratch initialization, split/cohort and
no-future-leakage checks, D90 paired-norm provenance, B history indexing,
zero-init/evaluator compatibility, artifact persistence, and selector output
checks before that pest can enter its remaining 14 cells. A failure stops only
that pest. It is investigated and reported without a protocol modification.

The full design has 7 pests x 3 structures x 15 year/seed cells = 315 Stage-2
training cells. Selector-only processing never retrains a Stage-2 checkpoint.
Outcomes are descriptive replication results and are not grounds for
retrospective tuning or automatic canonical promotion. These pests are
within-domain replication evidence, not multi-domain evidence.
