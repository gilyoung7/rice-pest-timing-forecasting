# lead_v3_final LiteRT reference / 기존 경량화 구현 참고본

이 디렉터리는 기존 **`lead_v3_final` 배포 모델**을 경량화했던 구현의
소스 참고본입니다. **최신 Canonical B + Selector T의 경량화 모델이나 배포판이
아닙니다.** 현재 저장소의 Canonical 코드·체크포인트·Release를 대체하지 않습니다.

이 소스만 clone하면 전체 추론이나 모델 변환은 실행되지 않습니다. 모델, 정규화,
정책, 원본 API, 원자료는 의도적으로 제외했습니다. 과거 경량화 정책을 최신
Canonical 평가에 자동 적용하면 안 됩니다.

## 구성과 출처

| 디렉터리 | 참고할 구현 |
|---|---|
| `api_handoff_litert_portable/` | 통합 CLI, XGBoost/LiteRT 추론, 단일·배치 요청, 전처리, fallback, I/O 문서와 테스트 |
| `tflite_conversion/stage2/` | 공통 Stage-2 wrapper, export, synthetic/real parity 검증, benchmark, 요약 코드 |
| `tflite_conversion/standalone_stage2/` | metadata/normalization 분리 패키징, 독립 LiteRT runtime와 테스트 |
| `tflite_conversion/bph_stage2/` | BPH 초기 prototype의 대체 경로 안내문 |
| `stage1_xgboost_migration/` | Stage-1 JSON export, calibration/gate 이관, 확률·경보 동등성 검증 코드 |
| `docs/` | 당시 변환·통합 방법과 검증 결과 보고서 |

기준은 기존 GPU 저장소의 **커밋된 소스**입니다. 미커밋 실험 변경과 `_patched`
배포본을 섞지 않았습니다. 정확한 커밋, 파일 SHA256, 제외 목록과 로컬 차이는
[SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json), [LOCAL_VARIANTS.md](LOCAL_VARIANTS.md)에
기록했습니다. 이전 README의 절대경로·크기·검증 수치는 당시 기록이며,
이 참고본의 현재 실행 가능성이나 재검증 결과를 뜻하지 않습니다.

요청 JSON과 작은 배치 입력 예시는 I/O 설명을 위해 포함했습니다. 배치 입력의
site ID는 `EXAMPLE_SITE_ID`로 바꿨습니다. 예시 응답·예측 CSV·실행 로그·생성된
manifest는 제외했으며, 출력 계약은
[API_INPUT_OUTPUT.md](api_handoff_litert_portable/docs/API_INPUT_OUTPUT.md)에 있습니다.

## Stage-1: XGBoost JSON 이관

1. `export_portable_models.py`가 기존 `.pt` 컨테이너에서 XGBoost 모델을 읽어
   `model.json`과 feature metadata로 분리합니다. 이 단계에는 원본과 호환되는
   PyTorch/XGBoost/scikit-learn 소스 환경이 필요합니다.
2. `export_calibration_assets.py`가 기존 temperature와 gate 설정을 옮깁니다.
   재적합 없이 기존 값과 feature 순서를 보존하는 것이 목적입니다.
3. 최종 API의 `infer/stage1_portable.py::PortableBranch`는
   `xgboost.Booster`로 JSON을 로드해 scikit-learn 및 `.pt` 로딩을 제거합니다.
   이전 `portable_stage1.py`는 sklearn wrapper를 사용하는 별도 중간 구현입니다.
4. 원본 확률 → calibration → k/threshold → 경보일 → dispatch를 차례로 비교합니다.
   표형 feature의 순서뿐 아니라 float32와 pandas/NumPy 메모리 배열 순서도
   보존해야 합니다. Gate JSON이 권위 자료이며 drift한 YAML을 대신 쓰면 안 됩니다.

관련 과거 검증:
[Stage-1 report](stage1_xgboost_migration/reports/alert_parity_report.md),
[integration report](docs/lightweight_api_integration_report.md).
보고서에는 합성 또는 다른 병해충 label을 차용한 검증도 포함되므로 범위를 확인하세요.

## Stage-2: TFLite/LiteRT FP16

`inference_model.py`는 `lead_v3_final`의 mu 계산 경로만 export-safe wrapper로
만듭니다. 기존 API가 사용하지 않는 hazard/PMF tail을 제외한 이 설계는
그 모델에 대한 판단입니다. 최신 모델에서도 필요 없다고 가정하면 안 됩니다.

`export_all.py`: `torch.export` → `litert_torch` → FP32/FP16 `.tflite`.
`validate_all.py`와 `validate_real.py`: 원본 → wrapper → LiteRT를 비교.
`standalone_stage2/build_package.py`: metadata와 `normalization.npz`를 분리.
`runtime/interpreter.py` 및 `infer/stage2_litert.py`: 독립
`ai_edge_litert.interpreter.Interpreter`로 입력 tensor를 bind하고 mu를 읽습니다.

기존 export는 **B=K=1**이며 BPH는 `(T,d_in)=(131,27)`, 나머지는 `(241,45)`입니다.
이 값, alert channel, 정규화 bypass, 입력 dtype 및 출력 DOY 변환은
기존 모델 계약이며 Canonical 모델에 그대로 쓸 수 없습니다.

기존 통합 API는 고정 offset, sigma=5, **95% 구간**과 병해충별 climatology
fallback을 사용합니다. BPH/WBPH가 learned 출력을 최종값으로 쓰고 나머지 6종은
climatology를 권장했던 정책입니다. **Selector T의 12개 후보/선택·shift와
Canonical 80% 구간 평가 정책을 구현한 배포판이 아닙니다.**

## 외부 의존성과 실행 불가 범위

| 기능 | 이 Git 업로드에 없는 필수 입력 |
|---|---|
| `.pt` → JSON export | 원본 Stage-1 checkpoint/기존 API ZIP, 호환 소스 환경 |
| `.pt` → LiteRT export/real parity | 원본 `api_handoff_transformer` 코드와 Stage-2 checkpoint, daily/LONG 입력 |
| standalone package build | 변환된 `.tflite`, checkpoint normalization/metadata, fallback policy |
| 통합 API build | Stage-1 JSON/calibration/gate/site_history, standalone Stage-2 산출물, 원본 정책·climatology |
| 통합 예측/asset-dependent tests | 구성 완료한 `assets/`, daily weather/LONG/site metadata/생육 정보 |

원본 API도 별도 외부 의존성입니다. 예를 들어 `stage2/checkpoint.py`는
이 참고 디렉터리 아래 `api_handoff_transformer/infer/ckpt.py`를 import하며,
Stage-1 `common.py`는 부모 디렉터리의 ZIP/API를 참조합니다.
이 경로는 역사적 구현 그대로 보존했습니다. 중첩 배치된 현재 위치를 기준으로
명시적으로 경로를 설정·수정해야 합니다. `build_package.py`의 출력 경로도
검토하고, 기존 운영 폴더를 대상으로 실행하지 마세요.

- Runtime: [requirements-runtime.txt](api_handoff_litert_portable/requirements-runtime.txt)
  (`xgboost`, `ai-edge-litert`, `numpy`, `pandas`, `PyYAML`). 원래 런타임은
  PyTorch/TensorFlow/scikit-learn을 요구하지 않습니다. Linux의 XGBoost는
  scipy/NCCL 같은 전이 의존성 때문에 설치 크기가 클 수 있습니다.
- Conversion: [requirements-tflite.txt](tflite_conversion/stage2/requirements-tflite.txt).
  런타임 환경과 분리하며, 기록된 macOS/arm64 버전을 최신 Linux 호환성
  검증으로 해석하지 마세요.
- Migration source/test: `stage1_xgboost_migration/requirements-*.txt`,
  `api_handoff_litert_portable/requirements-test.txt`.
- 실제 날씨 API 호출과 HTTP 서버는 구현되지 않았습니다. `infer/providers.py`의
  CSV/DataFrame provider가 연결 지점입니다. CLI는 모델과 입력을 준비한 후
  `python api_handoff_litert_portable/run_predict.py --input-dir IN --output-dir OUT`로
  호출하는 구조입니다. 이 참고본만으로는 위 명령을 실행할 수 없습니다.
- CPU 단위 테스트용 코드도 포함했지만, 실제 모델을 import/실행하는 테스트와
  asset-dependent integration test가 섞여 있습니다. 전체 pytest를 asset-free
  검증으로 간주하거나 기존 assets를 붙여 무작정 실행하지 마세요.

## 후임 연구원: Canonical B + Selector T에 적용할 때

1. **출처와 Lock 확정:** 해당 Canonical checkpoint, Stage-1 Gate·선정 seed,
   정규화·feature 순서, Selector 모델/전처리, shift를 SHA256으로 고정합니다.
   `lead_v3_final` 자산과 새 Canonical 자산을 혼용하지 않습니다.
2. **모델 wrapper 재작성:** B의 shared multi-offset encoder, recent/history
   branch, learned gate, offset별 mu head 및 실제 사용되는 출력 경로를 반영합니다.
   레거시 단일 mu wrapper나 B=K=1 가정만으로 최신 구조가 보존되지는 않습니다.
3. **입력 계약 이관:** checkpoint별 geometry, neighbor/history/dispatch 채널,
   missing indicator, 인과 마스킹과 학습 시 normalization/bypass를 재현합니다.
   이 참고본의 27/45채널이나 14 dispatch 값을 새 스키마로 가정하지 않습니다.
4. **Selector T 포함:** 동결된 LightGBM 모델 5개, 20개 특성의 정확한 순서
   (`mu_position` 포함), 학습된 imputer, offset 후보, tie-break 및
   validation-selected shift를 유지합니다. 기존 fixed-offset/fallback 정책으로
   대체하거나 2025 결과로 다시 선택하지 않습니다.
5. **구간·정책 이관:** Canonical의 80% 구간 계산, ensemble/seed 집계,
   alert/cohort/시즌 경계 및 proxy 구분을 그대로 유지합니다. 레거시 95%/sigma=5
   정책을 자동 적용하지 않습니다.
6. **후속 검증:** 원본 tensor/정규화 → FP32 wrapper → LiteRT FP32/FP16 →
   Selector의 선택 offset → 최종 구간을 단계별 비교합니다. tolerance는 사전에
   정하고, 양성 부재의 예측과 정확도 N/A를 구분합니다. 이 업로드에서는
   이러한 변환·추론·성능 검증을 실행하지 않았습니다.

## 소스 전용 배포 경계

`assets/`, `artifacts/`, checkpoint/JSON 모델, 실제 관측/기상 자료, calibration/
normalization 산출물, site_history, 캐시, fixtures, venv, archive 및 인증정보는
포함하지 않았습니다. 관련 경로는 `.gitignore`로도 제외합니다.
모델 공급과 최신 Canonical 변환은 후속 별도 작업입니다.

기존 저장소의 루트 README, Canonical 코드 및 Release는 변경하지 않습니다.
