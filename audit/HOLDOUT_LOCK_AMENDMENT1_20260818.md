# HOLDOUT LOCK AMENDMENT 1 — 2026-08-18

This amendment corrects the future-year temporal-holdout premise in [EXPB verdict](EXPB_VERDICT_20260817.md). The original HOLDOUT LOCK text is preserved in that document without deletion or strikethrough and is marked with a reference to this amendment.

2025 및 2026 연도 데이터는 본 프로젝트에 존재하지 않으며, 확보가 확인된 적도 없다. 미래 연도 holdout의 존재는 확보 여부를 확인하지 않은 채 연구 설계 과정에서 잘못 전제된 것으로, 데이터 확보 무산이 아니라 설계 오류의 정정이다. 따라서 '2026 one-shot 개봉'을 전제한 조항들은 현재 실행 불가능하며 효력을 갖지 않는다.

본 절의 LOCK 항목 목록(architecture / loss / metric / selector / seed ensemble / checkpoint selection / inference / bin definitions / no-more-dev-tuning 선언 / one-shot 조항)은 향후 독립 데이터(새 연도, 신규 지역, 외부 도메인 confirmatory set)가 실제로 확보될 경우 재사용할 GOVERNANCE TEMPLATE으로 보존한다.

이에 따라 2022–2024 결과의 지위를 다음으로 확정한다:

- WBPH 계열 결과: temporally valid development evaluation (fold 내부 label 위생은 유지되었으나 모델 계열 선택이 해당 결과를 조건으로 이루어짐; selection-aware estimate)
- 7-pest 결과: frozen-protocol within-domain replication (프로토콜은 WBPH에서 동결 후 무튜닝 전이; 단 8개 pest는 동일 연도·기상 covariate를 공유하므로 독립 replication 8건이 아니며 유효 n < 8)

어떤 문서에서도 2022–2024 수치를 무수식 'test performance' 또는 'final holdout result'로 표기하지 않는다.
