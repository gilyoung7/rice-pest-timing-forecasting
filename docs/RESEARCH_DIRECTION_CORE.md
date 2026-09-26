# RESEARCH_DIRECTION_CORE

## 1. Current empirical starting point

### Established evidence

- Extending the Stage-2 context from D28 to D90 improved the canonical 15-cell macro `IoU80_overall_tol0` from `0.3233106666666667` to `0.3789493333333333` (`Δ=+0.055638666666666683`). D90 contains D28's recent-context information as a strict input subset. [D90 decision](audit/D90_CANONICAL_DECISION.md)
- This overall gain was not uniform: the recorded D90-versus-D28 subset deltas were `≤60: −0.059`, `61–75: +0.136`, and `>75: +0.219`. Thus more context improved long-lead regimes while degrading the short-lead regime. [D90 decision](audit/D90_CANONICAL_DECISION.md)
- The early-stopping/truncation explanation was audited and rejected. [EARLYSTOP audit](audit/earlystop_audit_20260815/EARLYSTOP_AUDIT_REPORT.md)
- Experiment B used an unchanged recent 28-day branch plus a separate 29–90-day history branch, with zero-initialized gated residual fusion. B is the current canonical Stage-2 model, improving D90 from `0.3789493333333333` to `0.4496573333333333`. [canonical declaration](audit/CANONICAL.json), [B verdict](audit/EXPB_VERDICT_20260817.md)
- B recovered short-lead performance and preserved/improved long-lead performance under the preregistered checks: `≤60 Δ(B−D90)=+0.068807`, `>75 Δ(B−D90)=+0.122891`. Seed instability was reduced but not eliminated: `SD[Δ(B−D28)]=0.0924334132`, compared with the prior D90 reference `0.102`. [B verdict](audit/EXPB_VERDICT_20260817.md), [D90 decision](audit/D90_CANONICAL_DECISION.md)
- M4 does **not** support simple lead-conditioned routing: scalar gate means were nearly flat across official true-lead bins (`0.786 / 0.792 / 0.795`). This does not establish that history contribution is flat, because the injected term is `g · W(h_h)`, not `g` alone. [B verdict](audit/EXPB_VERDICT_20260817.md), [B post-hoc](audit/EXPB_POSTHOC_20260817.md)
- D28/D90/B selector-oracle analyses show that candidate quality and selection headroom also matter. An oracle gap is a noise-containing, selection-based upper bound; it is not fully recoverable performance. [D90 decision](audit/D90_CANONICAL_DECISION.md), [SELGAP diagnostic](audit/selgap_diag_20260818/SELGAP_DIAG_REPORT.md)

### Current interpretation

The empirical result is a regime trade-off under context extension, followed by an improvement from separating local and historical processing. It is not yet a causal mechanism result.

### Cross-pest frozen replication

The frozen replication used the same D28 → D90 → B → `mu_position` selector
progression in seven newly trained, non-WBPH pests. The pest-wise table—not a
pooled average—is primary. The pooled values below are secondary references:
`D90−D28 = +0.005` (essentially neutral), `B−D90 = +0.069`, and selector
improvement over B `= +0.073`. [cross-pest report](rice/outputs_crosspest_frozen_replication_20260818/audit/CROSSPEST_FROZEN_REPLICATION_REPORT.md)

| Observation | Cross-pest replication | Including original WBPH anchor |
|---|---:|---:|
| D90 seed-SD increase | 7/7 | 8/8 |
| B mean improvement | 7/7 | 8/8 |
| selector (`mu_position`) improvement | 7/7 | 8/8 |
| B recovery pattern (exploratory definition) | 7/7 | 8/8 |
| D90 mean reversal | 4/7 | 5/8 |
| B variance mitigation | 2/7 | 3/8 |

*Count convention for this table: “cross-pest replication” is the seven new
pests only; “including original WBPH anchor” adds the original WBPH result.
The B recovery/reversal class thresholds were defined after the frozen
replication and are exploratory, not confirmatory or eligible for promotion.*

Lead-bin coverage is uneven in several pests: for example, BPH has only 5/15
non-empty cells in the `>75` bin (and 10/15 in `61–75`); consequently its
reversal “not reproduced” classification is close to a withholding judgment,
not strong negative evidence. The full coverage table and pest-wise values are
in the [cross-pest report](rice/outputs_crosspest_frozen_replication_20260818/audit/CROSSPEST_FROZEN_REPLICATION_REPORT.md).

## 2. Core research reframing

The core contribution should **not** be framed as: “we invented a gated dual-branch architecture.”

The research question is instead: **More temporal context is not always better: extending context can improve some regimes while degrading others despite containing all shorter-context information.**

Working theme: **context-extension interference and separated residual context injection**.

Possible paper-level framing: *When does additional temporal context interfere with local predictive structure, and can separated residual context injection stabilize long-context learning?*

Novelty is **not yet established**.

## 3. Research questions

D90의 short-lead failure는 단일하지 않다: point-location이 훼손되는 pest와, 중심은 유지·개선되나 interval 층만 훼손되는 pest가 공존한다. B는 이 이질적 phenotype 전반을 개선한다. 따라서 RQ4는 monolithic context extension이 왜 이질적 failure mode를 만들고 separated pathway가 왜 그 전부에 걸쳐 개선되는지를 묻는다 (exploratory).

**RQ1.** Does increasing temporal context monotonically improve prediction?

**RQ2.** When a long-context model contains the short-context input as a strict subset, why can some prediction regimes degrade?

**RQ3.** Can local-context representations be protected while still exploiting long-range history through a separate residual pathway?

**RQ4.** Why does the D90 failure phenotype vary across pests, while the benefit of a separated history pathway generalizes across them?

Competing hypotheses include gradient interference reduction, representational protection, residual-path regularization, zero-init optimization anchoring, capacity allocation, implicit multi-scale representation, calibration/loss interaction, and sample-dependent contribution hidden in `W(h_h)`.

## 4. Primary working hypothesis: gradient interference

**WORKING HYPOTHESIS — not a conclusion.**

Existing development diagnostics show that `>75` samples had disproportionate loss and absolute-gradient fractions under the audited loss: sample fraction `0.2698`, loss fraction `0.5928`, and `|dL/dμ|` fraction `0.4324`. [pre-arm diagnostic](audit/DIAGNOSTIC_PRE_ARM_SELECTION.md)

A possible account is that D90 sends recent and older-history information through a shared encoder, allowing gradients associated with long-range prediction to interfere with representations useful for local prediction. B separates recent and history processing, begins in a D28-equivalent functional state (`W=0`), and can learn history contribution progressively through a residual path.

This does **not** mean history gradients are fully isolated. Because `g = f([h_r, h_h])` and the fused output depends on both branches, gradients can couple branches after initialization. The actual computation graph and autograd paths must be checked directly before making an isolation claim.

D90의 failure phenotype은 pest마다 이질적이지만 (mean reversal: cross-pest
replication 4/7, including original WBPH anchor 5/8; 순수 분산 팽창 등),
separated pathway의 mean improvement는 cross-pest replication 7/7,
including original WBPH anchor 8/8에서 일관된다. 또한 B의 variance 완화는
cross-pest replication 2/7, including original WBPH anchor 3/8에 그친다.
따라서 B를 D90의 short-lead interference를 막는 corrective mechanism으로
해석하기 어렵고, representation capacity allocation 또는 architectural
inductive bias 같은 failure-mode-independent mechanism은 가설로 유지하되
상대 우선순위가 상향된다. sheath_blight(reversal 있음+큰 개선)와
brown_spot(reversal 없음+큰 개선)의 대비는 B가 reversal 교정 단일 기능이
아님을 시사하나, 단일 failure-mode-independent mechanism의 확증은 아니다.
'zero-init residual path의 optimization 안정화' 단독 서사는 약화됨.

B outperformed D90 at the pest-level macro in cross-pest replication 7/7
pests and including original WBPH anchor 8/8 pests, but effect sizes were
heterogeneous (`+0.021` to `+0.126`). Therefore, the current evidence supports
a consistently positive directional effect across pests, not yet a uniformly
robust improvement within every pest. Pest-level paired-cell sign consistency:
brown_spot 15/15 (consistent within-pest); rice_stem_borer_2 9/15
(directional, cell-level consistency not established); rice_stem_borer_1 12/15
(consistent within-pest); sheath_blight 14/15 (consistent within-pest); blast
11/15 (consistent within-pest); BPH 7/15 (directional, cell-level consistency
not established); bacterial_blight 10/15 (directional, cell-level consistency
not established); WBPH anchor 9/15 (directional, cell-level consistency not
established). These are fixed-seed (`20260818`), 10,000-resample cell-bootstrap
summaries. [paired consistency table](rice/outputs_crosspest_frozen_replication_20260818/audit/CROSSPEST_PAIRED_CONSISTENCY_B_MINUS_D90.csv)

For BPH, the bootstrap 95% CI of the mean paired Δ includes zero
([−0.046, +0.090], median −0.011); the effect for this pest is unresolved
rather than directional.

Across pests, cell-level consistency tracks effect size; no pest shows an
established negative effect. B's improvement is established where it is large,
and unresolved — not refuted — where it is small (15 cells cannot resolve
effects of ~+0.02 given cell SDs of 0.04–0.20).

## 5. Competing explanations

- gradient interference / optimization conflict;
- representational interference or drift in a shared long-context encoder;
- regularization from a separated residual pathway;
- optimization anchoring caused by zero initialization;
- capacity/allocation effect rather than gating;
- implicit ensemble or multi-scale representation effect;
- calibration/loss interaction;
- genuinely sample-dependent history contribution in `W(h_h)`, despite nearly flat scalar `g`.

Exploratory cross-pest observation: reversal-reproducing pests include strong
D28 baselines for sheath_blight (`0.378`) and blast (`0.396`), compared with
rice_stem_borer_2 (`0.245`) and BPH (`0.269`); bacterial_blight (`0.338`) is
an exception. This is an eight-point descriptive association, not an estimated
effect or a mechanism result. It motivates including local-signal strength as
an explicit axis in the synthetic study. It does not align with cell-level
consistency: brown_spot has no D90 reversal reproduction but is 15/15
consistent for B−D90.

The regime-balanced-loss hypothesis remains live and is not prematurely eliminated.

## 6. Immediate low-cost mechanism analyses

These analyses must not modify the canonical model.

### A. Effective history contribution

Measure `r = ||g · W(h_h)|| / ||h_r||` and report it by lead bin, year, seed, positive-B-versus-D90 cells versus negative cells, and successful versus unstable runs if a predeclared definition exists. Also inspect the direction/cosine between `h_r` and `gW(h_h)`, not only its norm.

### B. Gradient analysis

Measure gradient conflict/cosine for short-lead versus long-lead subsets, for recent-path versus history-related signals where technically well-defined, and for D90 versus B. Do not invent a decomposition the computation graph does not support.

### C. Representation analysis

Compare D28, D90, and B for representation drift from D28, effective rank, probe accessibility, and seed variance. Distinguish information being absent from information being linearly less accessible.

## 7. Context-length dose-response experiment

After the applied track closes, test context lengths `28 / 45 / 60 / 75 / 90`; extend further only with justification. Measure overall performance, official lead-bin performance, seed variance, gradient conflict, and representation drift. The goal is to determine whether degradation is gradual, thresholded, or tied to availability of particular historical regimes.

## 8. Synthetic minimal-reproduction study

Construct a controlled time-series task with a strong recent/local signal, a weaker long-range signal, controllable long-range distance and strength, controllable noise, and controllable regime conditionality:

1. long-range signal always useful;
2. long-range signal useful only in a subset of regimes.

Compare a short-context model, a monolithic long-context model, and a separated-history residual model. Add simple controls only when needed to discriminate mechanisms.

Falsifiable predictions:

1. If long-range information is always useful and compatible with local signal, monolithic long-context degradation should be smaller.
2. As long-range signal becomes more regime-conditional, gradient conflict and seed instability in the monolithic model should increase.
3. If separated residual context injection addresses interference, its relative advantage should increase in the conditional/interfering regime.

Failure of these predictions weakens the working hypothesis.

## 9. Generalization requirements for an AI-core paper

The cross-pest replication is not multi-domain evidence. These pests are
within-domain robustness evidence because they share agricultural/weather
covariates, similar temporal structure, and a common pipeline. A core-AI claim
requires validation on genuinely different temporal problems.

Possible examples—not commitments—include predictive maintenance/failure forecasting, medical time series, and other event-timing or long-context temporal tasks. Datasets must be separately researched before selection.

## 10. What is NOT currently justified

- claiming a novel architecture from the current B design;
- claiming flat scalar `g` means history usage is constant;
- claiming gradient interference has been proven;
- claiming an oracle gap is recoverable;
- claiming the cross-pest replication establishes multi-domain generalization;
- claiming cross-attention is the obvious next step.

## 11. Current execution order

1. selector round 1 / `mu_position` work;
2. freeze the applied model/selector decision;
3. if independent data is actually secured, apply the HOLDOUT LOCK AMENDMENT 1 governance template;
4. only then begin the AI-core mechanism track: contribution analysis → gradient analysis → context sweep → synthetic study → external-domain replication.

Selector work is downstream candidate selection. It must not be used as evidence for or against the Stage-2 optimization mechanism unless a direct connection is demonstrated.

Cross-pest replication 7/7 and including original WBPH anchor 8/8 dev-period mean improvement는 B+selector가 dev overfitting의 산물일 사전 확률을 낮추지만, 이는 독립 검증이 아니며 본 결과가 향후 독립 데이터에서의 성능을 보증하지 않는다. 2022–2024 WBPH 결과는 selection-aware temporally valid development evaluation이고, 7-pest 결과는 frozen-protocol within-domain replication이다; [HOLDOUT LOCK AMENDMENT 1](audit/HOLDOUT_LOCK_AMENDMENT1_20260818.md)을 따른다.

## 12. Decision rule for pursuing the core-paper track

Escalate seriously toward a core paper only if all of the following accumulate:

- context-extension degradation reproduces beyond the original task;
- degradation correlates with a measurable optimization or representation phenomenon;
- the separated-residual approach consistently mitigates both performance loss and instability;
- the effect reproduces in controlled synthetic settings; and
- at least one genuinely external domain reproduces the phenomenon.

Otherwise retain this work as a strong domain/modeling insight rather than forcing a core-AI claim.
