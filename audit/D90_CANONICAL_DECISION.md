# D90 canonical baseline decision

Decision date: 2026-08-17. Status: **D90 is the canonical baseline.** This does not change the already-GO D90 decision.

## Official metric definition

headline metric = IoU80_overall_tol0: selected candidate의 iou80_geom에 lateness mask (eval_doy > true_onset_doy → 0) 적용, selector 5-seed의 per-sample 평균 → 셀 내 sample 평균 → 15셀 (year 3 × Stage-2 seed 5) macro 평균.

Fixed recorded values, reproduced by reading the 15 official pooled CSVs: D28 = 0.3233106666666667, D90 = 0.3789493333333333, Δ = +0.055638666666666683. All subsequent paired comparisons use this definition as the sole primary metric.

## Canonical declaration and governance

[CANONICAL.json](CANONICAL.json) is the sole canonical-baseline declaration. It is reference-only: no existing code automatically reads it or changes behavior from it. Future experiment preregistrations gain its effect only by explicitly citing it.

The declaration may change only with a decision document and an appended history entry. The D28 official directory remains in place and is FROZEN for possible multi-scale reuse; its complete SHA256 manifest is [d28_frozen_manifest.txt](d28_frozen_manifest.txt).

## v2 contamination event and v4 revalidation

- The v2 wrapper had a one-slot arm-path-constant error: its “D28” slot loaded asym5_max75, while its “D90” slot loaded asym5_max140 (the actual official D28).
- G1 initially failed to detect this because it compared against the copied replay CSV itself: circular validation.
- The issue was detected through the METRIC_RECON 0.322/0.379 discrepancy, then a 15/15 exact-match comparison, and was localized by REPLAY_FORENSIC 1 and 2.
- All v2/v3-based analysis, including the initial BLEND_DIAG judgment, is invalid for official D28/D90 comparison. Both locations carry DEPRECATED markers.
- v4 hard-coded the official source absolute paths and passed all three gates: G-A source SHA, G-B 30 cell-level |Δ| = 0.0 plus the macro values above, and G-C non-identical D28/D90 per-sample vectors with zero cohort mismatch.

Lesson: a bitwise gate is valid only when its comparison target’s absolute path is explicitly the official directory; a copied self-reference is not an independent gate. Apply this rule to every later gate.

## Follow-up experiment decision

Valid BLEND_DIAG v4 results from [AMENDMENT1_REPORT.md](sample_dump_v4_20260817/AMENDMENT1_REPORT.md):

- R1 FAIL: canonical gate Δ = +0.008021, below +0.015; nevertheless a positive routing signal exists (fake-pair −0.0284 reversed sign; real layer +0.0136).
- R2 FAIL: LOYO endpoint-proxy blend Δ = −0.004680. PMF-level mixture was not evaluated, so this is an endpoint-proxy limitation.
- R3 FAIL: D90 subset slope spread = 0.272133, not <0.05. D90 slopes improve in all subsets: 0.221→0.482, 0.537→0.754, 0.082→0.742. The ≤60 deterioration is therefore consistent with over-response/dispersion, not simple dulling.
- R4 PASS: oracle–gate gap = 0.090626 (≥0.03 with R1 failing).

Decision: prioritize Experiment B — D28 encoder + 29–90 day history branch + zero-init soft gate. Experiment A (regime-balanced loss) remains a live competing hypothesis and will be reassessed after B. The hidden-memory cache design is discarded because its opaque state is not an auditable causal routing signal under the frozen baseline contract.

## Known limits for Experiment B interpretation

Seed instability is Δ SD 0.102. Subset deltas are ≤60 −0.059, 61–75 +0.136, and >75 +0.219. The hard-routing oracle ceiling 0.478 is a noise-containing selection upper bound, not a fusion-performance estimate.

## Input integrity

Official-directory aggregate SHA256s before and after this declaration were unchanged:

| directory | aggregate SHA256 |
|---|---|
| D28 | 129e8509789edc87f3fe92097c03a5a5f7373576de9572ef59dea04efe6968b4 |
| D90 | 412a5dfd2829d25f687454faf757839190a7963f9989518c16ff0b25ca53d716 |

Related-document SHA256:

| document | SHA256 |
|---|---|
| audit/D90_ABLATION_PLAN.json (D90 preregistration) | 276981d0e54edf2a6a99f8a4e754c6b716c416d5a49bab8dfc751900405cdc6b |
| audit/earlystop_audit_20260815/EARLYSTOP_AUDIT_REPORT.md | f14518d24a24938a9d8bae50009e6e500248b622aa4bc86c88517d621b706a65 |
| audit/replay_forensic_20260817/FORENSIC_REPORT.md | 3c0c428460ecb8436f5d92b6174da256cb4c54662da71d9d6604c382b786d36d |
| audit/sample_dump_v4_20260817/FORENSIC2_REPORT.md | 088aa2ff75da332f4048fc6fbb832616bb3d0d1b39fdb168368dccb95e2ee520 |
| audit/sample_dump_v4_20260817/SAMPLE_DUMP_V3_REPORT.md | 5eea94e87fff6a48de1f3e4f846578b134c0f20dffefb0c0caf808388370adcc |
| audit/sample_dump_v4_20260817/AMENDMENT1_REPORT.md | dffd4221f8edd2b177a2ecff973cd5a7716dd3c6d9b9f0e55323b24338a6ddcd |
