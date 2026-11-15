# Stage-2 FP32/FP16 conversion and parity reference

This is the historical **lead_v3_final** mu-only conversion implementation.
For scope, external assets, Canonical B/T adaptation and reading order, start at
[the reference README](../../README.md). It does not convert Canonical B unchanged.

Read the files in this order:

1. `pest_configs.py`: expected legacy geometry, smoke records and policy offsets.
2. `checkpoint.py`: external original loader, strict state/config/weight checks,
   original mu and synthetic input construction.
3. `inference_model.py`: export-safe mu wrapper and `load_and_wrap`.
4. `export_all.py`: wrapper equality gate, LiteRT conversion and FP16 recipe.
5. `validate_all.py`: original/wrapper/FP32/FP16 parity and tolerances.
6. `validate_real.py`: original real preprocessing + real-data parity; imports
   helpers from `validate_all.py`, which therefore must remain alongside it.

External `api_handoff_transformer/infer/ckpt.py`, `infer/preprocess.py`,
checkpoints/policy/dispatch, weather and LONG files are not included.
Use a separate conversion environment described by `requirements-tflite.txt`;
its historical pins are not a fresh compatibility guarantee for current Linux.
The old path assumptions require review after nesting this reference directory.

Once external source/assets are deliberately supplied, historical entry points
are `export_all.py`, `validate_all.py --seeds 8`, and
`validate_real.py --daily-master PATH --long-dir DIR`. None were run for this
cleanup. Full model-dependent execution is unavailable from this Git snapshot.

The latency benchmark and report-merging scripts are omitted from the minimal
reference. They are not dependencies of the retained implementation. Their
original source and results remain in the initial upload commit and in the
[all-pest conversion report](../../docs/all_pests_stage2_tflite_conversion_report.md).
The report describes the historical 8-pest validation, B=K=1 export limitation,
FP16 tolerances and legacy policy; it is not a Canonical B/T acceptance result.
