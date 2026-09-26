#!/usr/bin/env python
"""E5d clean-selection training launcher.

Restricts the trainer's VALIDATION set to the fold's val_ckpt sample IDs so that the
checkpoint (best raw val_iou80) is selected on val_ckpt ONLY -- val_fit and val_cal are
never seen by training. Achieved by patching rice.src.dataset.split_samples BEFORE
src.vendor.run_train imports it (run_train does `from rice.src.dataset import split_samples`,
so the name is bound at import time to whatever the attribute is then). NO existing file is modified.

Usage (invoked by train_clean_fold.sh):
  python _patched_train.py --eval_year 2022 --assign /path/split_assignment.json -- <run_train args...>
"""
import argparse, importlib, json, os, runpy, sys
from pathlib import Path

# ---- canonical module source -------------------------------------------------------------
# Previously an external workspace and an unrelated checkout were pushed ahead of PYTHONPATH,
# so src.vendor.* came from that workspace while the grid process imported the in-repo copy:
# two physical copies of model.py on the two sides of one experiment. This repository is now
# the single canonical source for both processes.
VENDOR = Path(__file__).resolve().parent                 # <repo>/rice/experiments/allpests_e5d/vendor
REPO = VENDOR.parents[3]                                 # <repo>
for _p in (str(REPO), str(VENDOR)):                      # vendor first (src.*), repo next (rice.*)
    while _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

# rice.configs.base in this repository relocates the external data tables through two env vars.
# Every previous run read the compiled-in defaults. Silently clearing an inherited value would
# hide the fact that someone intended different data, so a set value is a contract violation and
# aborts. Only the verified-unset fact is recorded.
DATA_PATH_ENV_VARS = ("RICE_DAILY_CSV", "RICE_LONG_BY_PEST_DIR")
_set = {v: os.environ[v] for v in DATA_PATH_ENV_VARS if v in os.environ}
if _set:
    raise SystemExit(
        "[abort] DATA PATH ENV CONTRACT VIOLATION: "
        + ", ".join(f"{k}={v!r}" for k, v in _set.items())
        + " -- these relocate the external data tables away from the defaults every previous "
          "run used. Unset them explicitly before launching, or register the new paths.")
DATA_PATH_ENV_VERIFIED_UNSET = {v: None for v in DATA_PATH_ENV_VARS}
print(f"[canonical] repo={REPO} vendor={VENDOR}", flush=True)
print(f"[canonical] data_path_env_verified_unset={list(DATA_PATH_ENV_VARS)}", flush=True)

CANONICAL = {"src.vendor.model": VENDOR / "src/vendor/model.py",
             "src.vendor.run_train": VENDOR / "src/vendor/run_train.py",
             "rice.src.train_eval": REPO / "rice/src/train_eval.py",
             "rice.configs.base": REPO / "rice/configs/base.py"}
for _n, _want in CANONICAL.items():
    _got = Path(importlib.import_module(_n).__file__).resolve()
    if _got != _want.resolve():
        raise SystemExit(f"[abort] CANONICAL SOURCE MISMATCH {_n}\n"
                         f"    loaded   {_got}\n    expected {_want.resolve()}")
    print(f"[canonical] {_n} -> {_got}", flush=True)
os.environ["E5D_DATA_PATH_ENV_UNSET"] = json.dumps(DATA_PATH_ENV_VERIFIED_UNSET)
# -------------------------------------------------------------------------------------------

ap = argparse.ArgumentParser()
ap.add_argument("--eval_year", type=int, required=True)
ap.add_argument("--assign", required=True, help="split_assignment.json from make_splits.py")
ap.add_argument("rest", nargs=argparse.REMAINDER, help="-- then the run_train args")
a = ap.parse_args()
rest = a.rest[1:] if a.rest and a.rest[0] == "--" else a.rest

assign = json.loads(Path(a.assign).read_text())[str(a.eval_year)]
KEEP = {s for s, b in assign.items() if b == "val_ckpt"}
if not KEEP:
    raise SystemExit(f"[abort] no val_ckpt ids for eval_year={a.eval_year}")

import rice.src.dataset as DS
_orig = DS.split_samples

def _sid(s):
    return f"{s['site_id']}-{int(s['year'])}"

def patched_split_samples(samples, *args, **kw):
    tr, va, te = _orig(samples, *args, **kw)
    va2 = [s for s in va if _sid(s) in KEEP]
    print(f"[clean-split] val restricted to val_ckpt: {len(va)} -> {len(va2)} samples "
          f"(eval_year={a.eval_year}, val_ckpt ids={len(KEEP)})", flush=True)
    if not va2:
        raise SystemExit("[abort] val_ckpt filter produced an EMPTY validation set")
    return tr, va2, te

DS.split_samples = patched_split_samples          # patch BEFORE run_train imports it

sys.argv = ["run_train"] + rest
print(f"[clean-train] eval_year={a.eval_year} val_ckpt={len(KEEP)} ids; argv={' '.join(rest[:6])} ...", flush=True)
runpy.run_module("src.vendor.run_train", run_name="__main__")
