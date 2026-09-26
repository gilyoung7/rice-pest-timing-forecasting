# SELROUND1 verdict — B + selector v2 (`mu_position`)

Scope: selector-only paired evaluation on frozen B grids and checkpoints. No Stage-2 training, checkpoint access for inference, grid regeneration, or offset change was performed.

## Primary decision

| item | value | preregistered criterion | result |
|---|---:|---|---|
| S0 macro | 0.44965733333333335 | canonical 0.4496573333333333 | PASS |
| S0 `|Δ|` | 5.551115123125783e-17 | ≤ 1e-6 | PASS |
| T macro | 0.5437853333333333 | reference | — |
| Δ(T−C) macro | +0.0941280000000000 | ≥ +0.020000 | PASS |
| positive cells | 15/15 | ≥ 9/15 | PASS |
| Primary | GO | both required conditions | GO |

The original finalizer contained a non-preregistered per-cell comparison to the canonical **macro**; it was removed. The S0 gate is the preregistered 15-cell macro check above.

## Cell-level primary table

```csv
year,seed,C,S0,T,T_minus_C,S0_minus_canonical
2022,0,0.4217799999999999,0.4217799999999999,0.4826800000000001,0.06090000000000023,-0.02787733333333342
2022,1,0.3453799999999999,0.3453799999999999,0.46694,0.12156000000000011,-0.10427733333333339
2022,2,0.46288,0.46288,0.54902,0.08613999999999994,0.013222666666666716
2022,3,0.4154,0.4154,0.48812,0.07272,-0.034257333333333306
2022,4,0.5704,0.5704,0.64868,0.07828000000000002,0.12074266666666672
2023,0,0.44188,0.44188,0.5639600000000001,0.12208000000000013,-0.007777333333333303
2023,1,0.41464,0.41464,0.55458,0.13993999999999995,-0.03501733333333329
2023,2,0.4208599999999999,0.4208599999999999,0.52552,0.10466000000000009,-0.028797333333333397
2023,3,0.42318,0.42318,0.58674,0.16356000000000004,-0.026477333333333297
2023,4,0.4370200000000001,0.4370200000000001,0.5636800000000001,0.12666,-0.012637333333333223
2024,0,0.45316,0.45316,0.48834,0.03517999999999999,0.0035026666666667094
2024,1,0.38594,0.38594,0.47284,0.08689999999999998,-0.06371733333333329
2024,2,0.46658,0.46658,0.5626800000000001,0.09610000000000007,0.016922666666666697
2024,3,0.50132,0.50132,0.5595199999999999,0.05819999999999992,0.05166266666666669
2024,4,0.5844400000000001,0.5844400000000001,0.64348,0.05903999999999998,0.13478266666666677
```

## Secondary records (not primary decision rules)

### Official `L−alert_tstar` lead bins

```csv
lead_bin,C,S0,T,T_minus_C
61-75,0.4735409085414545,0.4735409085414545,0.5496402132316957,0.07609930469024118
<=60,0.4540589418714449,0.4540589418714449,0.5862458867991412,0.13218694492769634
>75,0.38870361208971804,0.38870361208971804,0.44299254496034746,0.054288932870629414
```

### Selector hit rates

```csv
arm,exact_hit,optimal_set_hit,regret
C,0.19342568032223204,0.2934394341290893,0.23793517190602947
S0,0.19342568032223204,0.2934394341290893,0.23793517190602947
T,0.422179978386875,0.513299440023578,0.1311860104575395
```

There are no worsened cells: all 15 `T−C` values are positive. The requested 2023 s1/s3 records are `+0.139940` and `+0.163560`, respectively.

Diagnostic consistency: diagnostic `mu_position` top-1 was `0.409319`; out-of-year realized T exact-hit is `0.422180`. T macro `0.5437853333333333` is below the recorded 2nd-best ceiling `0.576358057620599` and oracle `0.6777634519984965`.

mu_position captures a strong candidate-relative ordering signal; the hypothesis that it corrects a systematic early-bias in candidate μ is recorded as a mechanism hypothesis, not established.

## Separate observation: downstream candidate selection

Set-relative candidate information is an independent downstream-selection observation: candidate-set rank, rather than absolute μ, was a strong signal. It is not evidence for the context-interference research question and must not be used as such.

## Terminal clause

The preregistered single treatment is complete. No additional feature search or hyperparameter search was performed; the selector track is closed under the stated terminal clause.

Source tables: `audit/selround1_20260818/cells.csv`, `paired_cells.csv`, `lead_bin_delta.csv`, and `hit_rates.csv`. Preregistration SHA256: `88ca6af2839b03ae4cf58c6570091b208d745d48082f57d5363c4100a76a3535`.
