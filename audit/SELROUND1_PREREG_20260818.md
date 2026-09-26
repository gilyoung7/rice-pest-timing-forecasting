# PREREG — SELROUND1: selector feature 단일 추가 (`mu_position`)

확정일: 2026-08-18. 이 문서의 SHA256을 실행 전 기록하고, 변경 없이 실행한다.

## 0. 근거

SELGAP_DIAG의 S1은 PASS이다: adjusted gap은 0.1341, `mu_position` raw AUC는 0.7276 (`higher is better`, 방향 선택 없음), 단독 top-1 hit은 0.409이고 현 selector는 0.193이다. causality 검증은 완료되었으며 feature 입력에는 사후 정보가 없다.

Stage-2/B는 완전 동결한다. 이 작업은 selector 재학습만 수행한다.

## 1. Feature 정의

셀 `(year, Stage-2 seed)` 안에서 sample `s`, 후보 offset `o`에 대해:

`mu_position(s,o) = averageRank_{o' ∈ O_s}(μ_{s,o}) / |O_s|`

- rank는 `μ` 오름차순, 동점은 average rank이며 범위는 `(1/|O_s|, 1]`이다.
- infeasible offset의 `μ`는 같은 sample의 feasible 후보 `μ`를 기존 `_interp_mu`로 선형 보간한 값이다.
- 방향은 **higher is better**로 선고정한다. 평가는 `auc_higher_is_positive`만 사용하며 `best_direction` 계열은 금지한다.

## 2. 실험 설계

S0 선행 게이트: 기존 feature set과 공식 y−1 protocol로 selector를 재학습한다. 15셀 `IoU80_overall_tol0` macro는 canonical `0.4496573333333333`을 `|Δ| <= 1e-6`으로 재현해야 한다. 실패하면 실험은 무효이며 즉시 종료한다.

| arm | feature set | 목적 |
|---|---|---|
| S0 | 기존 feature set | canonical selector 재현 게이트 |
| C | S0와 동일 | paired control |
| T | 기존 feature + `mu_position` 1개 | 유일한 treatment |

불변 항목: LightGBM 설정, selector 5 seeds, y−1 fit, candidate set, offset 집합 `{3,7,14,21,28,30,35,42,45,49,56,60}`, B grid, Stage-2 checkpoint 전부. 파생 feature와 interaction은 금지한다.

## 3. 판정

Primary GO: `Δ(T−C) >= +0.020` 그리고 양수 셀 `>= 9/15`. 기대선은 macro `>= 0.4697`; 참고 상한은 2nd-best ceiling `0.576`이다.

Secondary (판정 아님, 보고 의무): exact/optimal-set hit rate 변화 (기준 `0.193/0.293`), 셀별 악화 목록—특히 2023 s1/s3의 Δ—및 공식 `L−alert_tstar` lead bin별 Δ.

GO여도 canonical 갱신은 별도 결정 문서에서만 한다. NO-GO면 selector 트랙을 종결하고 holdout 준비로 전환한다. 추가 feature 또는 hyperparameter 탐색은 금지하며, treatment 하나로 종결한다.

## 4. 출력·보호

출력은 `audit/selround1_20260818/` 아래에 S0/C/T 15셀 표, 판정표, inputs manifest를 남긴다.

금지: Stage-2 학습, checkpoint 접근, grid 재생성, offset 변경, commit, `git add -A`, reset, clean. 학습을 포함한 selector 단계는 host tmux에서 launcher script로만 실행한다.
