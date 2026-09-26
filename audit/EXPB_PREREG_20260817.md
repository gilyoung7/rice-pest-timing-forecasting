# Preregistration — Experiment B

Fixed date: 2026-08-17. Execution may begin only after the SHA256 of this file is recorded in EXPB_PREREG_20260817.sha256.

## Hypothesis and scope

H: separating days 29–90 into a history path and learning a per-sample soft injection gate will retain D90 long-lead benefit while reducing the ≤60 deterioration. This is one structural factor only. Initialization, normalization, loss, optimizer, schedule, selector, and evaluation protocol remain the D90 canonical protocol.

Evidence is limited to v4-valid results: R4 oracle gap 0.091; R1 has positive routing existence evidence (+0.008 canonical / +0.0136 real), not a pass; and R3 shows improved slopes in every subset. Experiment A (regime-balanced loss) remains a competing hypothesis. Hidden-memory cache is excluded because it provides no computational benefit and increases infrastructure cost.

## Fixed architecture

- X_recent = weather[t*-27 .. t*], exactly 28 days.
- X_hist = weather[t*-89 .. t*-28], exactly 62 days.
- For t* < 89, X_hist applies the same left-boundary handling as the D90 90-day implementation. T2 must prove this and zero future leakage at t*=28, 29, 89, 90.
- Encoder_D28 is the canonical D28 encoder unchanged, producing h_r.
- HistEnc: d_model=48, n_heads=4, n_layers=1; FFN, dropout, norm, positional encoding, and pooling match the canonical D28 encoder, producing h_h.
- Gate: g = sigmoid(Linear([h_r; h_h])), scalar per sample, with weight=0 and bias=0 (initial g=0.5).
- Fusion: z = h_r + g·(W @ h_h), with W=0 exactly at initialization. Thus z=h_r exactly at initialization.
- Existing offset and PMF heads are unmodified; only their input becomes z.

## Canonical protocol inherited from D90

Canonical reference: audit/CANONICAL.json, D90 official directory rice/outputs_allpests_e5d_d90_20260814.

Initialization extraction (D90 2022/seed0 hparams and train arguments):

- stage2_warm_start_ckpt is null and stage2_warm_start_seed is null: Experiment B uses scratch initialization, not warm start.
- New branch/gate tensors use the fixed zero initialization above. Existing D28-compatible tensors use the ordinary D90 scratch initialization; no D28 checkpoint weights are loaded for official training.

Normalization extraction:

- D90 uses stage2_frozen_norm_ckpt set to the paired D28 checkpoint for the same evaluation year and Stage-2 seed.
- Experiment B uses the same paired frozen-D28 normalization path and checkpoint persistence. X_hist uses the identical D90 29–90-day normalization protocol; no arbitrary D28/D90 norm mixing is permitted.

## Technical gates

T1: independently of official scratch init, load one D28 checkpoint and compare D28 forward to B forward with W=0 and gate init; grid predictions must agree at tol=1e-6.

T2: prove absolute X_hist indices and zero future leakage at t*=28, 29, 89, 90.

T3: record config and logs proving the normalization rule.

T4: sample_id and row count must exactly match the D90 grid cohort.

T5: persist source SHA, per-sample predictions, selector artifacts, and config in each grid output.

The 2022/seed0 smoke is technical only. If T1–T5 pass, run the remaining 14 cells automatically regardless of smoke performance. Any technical-gate failure invalidates the experiment.

## Fixed decision rules

Primary comparison is B versus D90, using CANONICAL.json and IoU80_overall_tol0, the 15-cell macro.

- GO: mean Δ(B−D90) >= +0.015 and positive cells >= 9/15.
- M1: ≤60 primary all-row Δ(B−D90) >= +0.030.
- M2: >75 primary all-row Δ(B−D90) >= −0.020.
- M3: Δ(B−D28) seed SD <= 0.102.
- M4: gate distribution versus true-lead bin is exploratory; a non-monotone pattern is not failure.

For ≤60, primary uses the canonical evaluator’s all-row IoU80 definition, including its own treatment of infeasible intervals; comparator-arm substitution is prohibited. A B/D90 both-interval-feasible complete-case value is sensitivity only. M1 uses the primary all-row value.

NO-GO with exactly one of M1/M2 successful is evidence for a cross-attention second stage. Fully neutral or worse results switch to Experiment A. No additional arm or hyperparameter search is allowed. The 15-cell result is terminal.

## Outputs and protections

Official output root: rice/outputs_allpests_e5d_expB_20260817/.

No writes to D28/D90 official directories; no loss, optimizer, schedule, or selector modification; no additional arm; no git add -A, reset, clean, or commit. Work runs only in tmux session expB_20260817.
