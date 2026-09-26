# Multi-pest assets (seven crosspest pests)

Scope: sheath_blight, bacterial_blight, brown_spot, rice_stem_borer_1, rice_stem_borer_2, BPH, blast
(status: `audit/CANONICAL_MULTIPEST.json`; decision: `docs/CANONICAL_MULTIPEST_DECISION.md`).
WBPH assets are unchanged and documented in DATA.md.

## 1. Release tars (two per pest)

Deterministic GNU tars (uid/gid 0, mtime 0, modes kept, C-sorted entries, files only), same
convention as the WBPH tars; extract at the repo root.

| tar | files | bytes | sha256 |
|---|---:|---:|---|
| `sheath_blight_core.tar` | 141 | 82,493,440 | `617862d5e8a90658d1b91426bd7dc55f54e878d8662126ada2cb44e4f06d5781` |
| `sheath_blight_retrain.tar` | 75 | 13,404,160 | `5cbc2bf11ce7a1d8d5be0929ea1a138a73dcd1d0fe3670683948277faa65c704` |
| `bacterial_blight_core.tar` | 141 | 35,788,800 | `419cbade667b46f2950f26cf6cf35154a840ed556e1022c48b40a279fb8b0eec` |
| `bacterial_blight_retrain.tar` | 75 | 13,158,400 | `dfaf01e917a33b2d30853a3e0167d52fc2d18490ac828bf8e9a4479f2903ae71` |
| `brown_spot_core.tar` | 141 | 50,104,320 | `e92bc5bd25e7742bf0756dced55131dff9d515263af7cd22f275e9d260d90af7` |
| `brown_spot_retrain.tar` | 75 | 13,342,720 | `2105f23f2b49658417c204fa3aa8efe373d2567ffcb272756590932830c4fc4d` |
| `rice_stem_borer_1_core.tar` | 141 | 26,931,200 | `80aa4f15c54152232519940d64c612572680ce627a6254d54e52db69e87daf28` |
| `rice_stem_borer_1_retrain.tar` | 75 | 13,199,360 | `29e76b2c60036737b4a42029b0fc9fa3daa61c250fab3a83b32b798c3b67b6f3` |
| `rice_stem_borer_2_core.tar` | 141 | 28,866,560 | `8a2176be804417ea7cab68f8649ee66fc303c1f377e7c9bf63bc459873a02fd4` |
| `rice_stem_borer_2_retrain.tar` | 75 | 13,189,120 | `e4b1ec246987bd5be4bae53cc30ec153167148fbe3446dfc57745db693284125` |
| `BPH_core.tar` | 141 | 25,538,560 | `ef860bad6d5a7f17635ee0e9c18a8f63f18da7941714e1bbcfc5523b22563263` |
| `BPH_retrain.tar` | 75 | 13,004,800 | `73520fa45ce504a54c3094e6a1e8aa33d51d8712afd6f1039e43efb671d01f20` |
| `blast_core.tar` | 141 | 49,715,200 | `68e04894af6d35926a031e14bde60cb35e205cf84e3bcfaa5dae970a5f351fe2` |
| `blast_retrain.tar` | 75 | 13,332,480 | `f77b9c872c89419a923ac8a8aac16ea0163a869749e6c9b6d5a52d204d6c23bb` |

- `<pest>_core.tar` (141 files) — needed for G0–G3 (grid + selector):
  - `rice/outputs_crosspest_frozen_replication_20260818/B/<y>/seed<s>/<pest>/clean/` — B checkpoint,
    `hparams.json`, `train_args.txt`, `train.log`, `diagnostics_v2/head_region_run4_seed<s>.jsonl`,
    3 split files (120)
  - `rice/outputs/stage2/<batch>/<pest>/` — frozen Stage-1 dispatch + climatology (6)
  - `reference/multipest/<pest>/grids/<y>/seed<s>/<pest>_E5d_clean_grid_1to75.csv` — reference copy of
    the canonical grids (15; G1 compares against `manifests/multipest/B_GRID_SHA256_<pest>.txt`)
- `<pest>_retrain.tar` (75 files) — B retraining inputs only, also read by G0 (D28 sha ↔
  `frozen_norm_source`): crosspest D28 checkpoints (15, frozen normalisation source) and D90
  `train_args.txt` + splits (60) under `rice/outputs_crosspest_frozen_replication_20260818/{D28,D90}/`.

The B directories intentionally contain no grid: `scripts/run_pest_b_grid.sh <pest>` regenerates it
there. Checkpoints store the original server's absolute dispatch path; `tools/pest_grid_reroot.py`
maps it into the repo and aborts on anything outside it.

Totals: 14 tars, 1,512 files, 7 × 216 per-pest files.

## 2. Verify

```bash
(cd /path/to/assets && sha256sum -c "$OLDPWD/manifests/multipest/RELEASE_ARCHIVES.sha256")
for t in /path/to/assets/*_core.tar /path/to/assets/*_retrain.tar; do tar -xf "$t"; done
for p in sheath_blight bacterial_blight brown_spot rice_stem_borer_1 rice_stem_borer_2 BPH blast; do
  sha256sum -c --quiet "manifests/multipest/RELEASE_ASSETS_$p.sha256" && echo "$p OK"; done
(cd data && sha256sum -c "$OLDPWD/manifests/multipest/RAW_DATA.sha256")   # daily table + 8 label files
```

## 3. Raw data (not redistributed)

Same data root as WBPH (`RICE_DATA_ROOT`, default `<repo>/data`): the daily table plus
`rice/LONG_by_pest/RICE_LONG_<Korean pest name>.csv` per pest (`rice/pests/<pest>/config.py: PATH_OBS`).
sha256: `manifests/multipest/RAW_DATA.sha256`.

## 4. Full crosspest outputs (provenance only)

The complete original directory (all four arms, selector outputs, logs, audit; 16,111 files) is not
part of the handoff release. It is preserved in the private archive repository
`gilyoung7/cropscience-research-archive`, Release `provenance-crosspest-frozen-20260818`:
`cropscience_crosspest_frozen_replication_20260818.tar` (1,359,431,680 B, sha256
`6518679a956245893af7f62b93c17c91abeafdaddd048a208e05915614b10a1d`) with a per-file sha256 list and restore
instructions (`ARCHIVE_README_crosspest.md`).
