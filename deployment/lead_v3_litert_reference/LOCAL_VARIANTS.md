# Source and local variant boundary

This reference copies committed blobs from `gilyoung7/cropscience`, commit
`98f45dbc597f81ca8b5a3721540b53355467883e`, without changing the original checkout.
The portable API last changed in committed history at `23cb3c3` (2026-07-22).
The working checkout is on an experimental branch; that branch name does not
change the historical `lead_v3_final` identity of these files.

## Uncommitted source changes excluded

Four portable API files currently differ from the source commit:
`run_predict.py`, `infer/stage1_portable.py`, `infer/_stage2_preprocessing.py`,
and `infer/_stage2_schema.py`. They add an A-only/no-occurrence-history path and
a variable dispatch-channel schema. They are outside this historical reference;
the working files and their changes are preserved. Both hashes are recorded in
`SOURCE_PROVENANCE.json`.

## Separate `_patched` directory

`/home/gpu4080/research/cropscience/api_handoff_litert_portable_patched/`
contains deployed FP16/JSON assets but a different runtime revision. No code or
assets from that directory are silently overlaid here. Per-file differences and
hashes of comparable source files are recorded in `SOURCE_PROVENANCE.json`.
During the preceding read-only audit, 88 model/normalization/metadata files and
9 supporting config/climatology files matched its historical manifest. That is
an asset-integrity check, not a fresh execution validation of this reference.

Historical conversion, migration and integration reports are copied under
`docs/` and `stage1_xgboost_migration/reports/`. Their results describe the
versions/environments named in those reports. Some reports predate later batch
fixes; they must not be read as a fresh acceptance result for this snapshot or
for Canonical B/T.

No training, conversion, model loading, inference or performance measurement was
run while preparing this reference. Only source/static and publication checks
are appropriate to this upload.

The compared committed version contains later generic-batch fixes in
`infer/batch.py`: input CSV path resolution, inheritance of per-row data paths,
and per-(pest, variant) context caching. These differ from the separate
`_patched` copy. `run_predict.py` itself is byte-identical between the committed
reference and that separate copy; its working-tree version is different and was
not copied. README/API-contract document revisions also differ, as listed in the
provenance file. The `_patched` label alone is not used as an acceptance claim.
