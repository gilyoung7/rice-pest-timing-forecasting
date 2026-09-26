#!/usr/bin/env python3
"""One SELROUND1 selector-only cell, copied from the validated replay path."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "rice/outputs_allpests_e5d_expB_20260817"
E5D = REPO / "rice/experiments/allpests_e5d"
PY = REPO / ".venv/bin/python"

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("S0", "C", "T"), required=True)
    ap.add_argument("--year", type=int, choices=(2022, 2023, 2024), required=True)
    ap.add_argument("--seed", type=int, choices=range(5), required=True)
    a = ap.parse_args()
    src = SOURCE / str(a.year) / f"seed{a.seed}" / "WBPH"
    dst_root = Path(__file__).resolve().parent / "runs" / a.arm / str(a.year) / f"seed{a.seed}"
    dst = dst_root / "WBPH"
    if dst.exists(): raise SystemExit(f"refusing existing output: {dst}")
    items = [src/"clean/grid/WBPH_E5d_clean_grid_1to75.csv", src/"clean/split_assignment.json", src/"clean/split_manifest.csv", src/"clean/split_overlap_checks.json"]
    if any(not p.exists() for p in items): raise SystemExit("missing frozen B grid/split input")
    (dst/"clean/grid").mkdir(parents=True)
    copied=[]
    for p in items:
        q = dst/"clean/grid"/p.name if p.parent.name == "grid" else dst/"clean"/p.name
        shutil.copy2(p,q); copied.append({"source":str(p),"destination":str(q),"sha256":sha(p),"copy_sha256":sha(q)})
    if not all(x["sha256"] == x["copy_sha256"] for x in copied): raise SystemExit("grid-copy SHA failure")
    env=os.environ.copy(); env.update({"ALLPESTS_OUT_ROOT":str(dst_root), "OUT_ROOT":str(dst_root), "PYTHONPATH":f"{E5D/'vendor'}:{REPO}", "WBPH_SHARED_MULTI_OFFSET":"1", "WBPH_MU_HEAD_MODE":"offset_specific", "WBPH_CANDIDATE_OFFSETS":"3,7,14,21,28,30,35,42,45,49,56,60"})
    if a.arm == "T": env["WBPH_SELECTOR_ADD_MU_POSITION"]="1"
    else: env.pop("WBPH_SELECTOR_ADD_MU_POSITION", None)
    subprocess.run([str(PY),str(E5D/"pest_eval.py"),"--pest","WBPH","--years",str(a.year),"--skip","dev"],cwd=REPO,env=env,check=True)
    metric = dst/"eval/clean_pooled_metrics.csv"
    if not metric.exists() or not (dst/"selector_artifacts_v2").exists(): raise SystemExit("missing selector output artifact")
    import pandas as pd
    value=float(pd.read_csv(metric).iloc[0].IoU80_overall_tol0)
    (dst/"cell_result.json").write_text(json.dumps({"arm":a.arm,"year":a.year,"seed":a.seed,"iou80_overall_tol0":value,"feature_mu_position":a.arm=="T","copied_inputs":copied},indent=2)+"\n")
    return 0
if __name__ == "__main__": raise SystemExit(main())
