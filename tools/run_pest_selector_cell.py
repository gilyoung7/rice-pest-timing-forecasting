#!/usr/bin/env python3
"""One selector-T cell for a crosspest pest: the per-cell recipe of
audit/selround1_20260818/run_selector_cell.py (WBPH, unchanged) with the pest as an argument.

Same frozen T protocol: copy the frozen B grid + splits (sha-checked), run pest_eval.py clean with
the E5d offset env and WBPH_SELECTOR_ADD_MU_POSITION=1, write cell_result.json (same schema + pest).
WBPH is refused here; it stays on the canonical runner.

usage: run_pest_selector_cell.py --pest P --year Y --seed S [--b-root DIR] [--runs-root DIR]
       run_pest_selector_cell.py --selftest
"""
import argparse, ast, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
E5D = REPO / "rice/experiments/allpests_e5d"
PY = REPO / ".venv/bin/python"
PESTS = ("sheath_blight", "bacterial_blight", "brown_spot", "rice_stem_borer_1",
         "rice_stem_borer_2", "BPH", "blast")
B_ROOT = REPO / "rice/outputs_crosspest_frozen_replication_20260818/B"
CANON_RUNNER = REPO / "audit/selround1_20260818/run_selector_cell.py"
# Frozen T protocol env, identical to CANON_RUNNER (checked by --selftest).
T_ENV = {"WBPH_SHARED_MULTI_OFFSET": "1", "WBPH_MU_HEAD_MODE": "offset_specific",
         "WBPH_CANDIDATE_OFFSETS": "3,7,14,21,28,30,35,42,45,49,56,60",
         "WBPH_SELECTOR_ADD_MU_POSITION": "1"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def cell_env(base, dst_root):
    env = dict(base)
    env.update({"ALLPESTS_OUT_ROOT": str(dst_root), "OUT_ROOT": str(dst_root),
                "PYTHONPATH": f"{E5D / 'vendor'}:{REPO}", **T_ENV})
    return env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pest", choices=PESTS, required=True)
    ap.add_argument("--year", type=int, choices=(2022, 2023, 2024), required=True)
    ap.add_argument("--seed", type=int, choices=range(5), required=True)
    ap.add_argument("--b-root", type=Path, default=B_ROOT)
    ap.add_argument("--runs-root", type=Path, default=None,
                    help="default outputs/multipest/<pest>/selector_T/runs")
    a = ap.parse_args()
    runs = a.runs_root or REPO / f"outputs/multipest/{a.pest}/selector_T/runs"
    src = a.b_root / str(a.year) / f"seed{a.seed}" / a.pest
    dst_root = runs / "T" / str(a.year) / f"seed{a.seed}"
    dst = dst_root / a.pest
    if dst.exists(): raise SystemExit(f"refusing existing output: {dst}")
    items = [src / f"clean/grid/{a.pest}_E5d_clean_grid_1to75.csv", src / "clean/split_assignment.json",
             src / "clean/split_manifest.csv", src / "clean/split_overlap_checks.json"]
    if any(not p.exists() for p in items): raise SystemExit("missing frozen B grid/split input")
    (dst / "clean/grid").mkdir(parents=True)
    copied = []
    for p in items:
        q = dst / "clean/grid" / p.name if p.parent.name == "grid" else dst / "clean" / p.name
        shutil.copy2(p, q); copied.append({"source": str(p), "destination": str(q), "sha256": sha(p), "copy_sha256": sha(q)})
    if not all(x["sha256"] == x["copy_sha256"] for x in copied): raise SystemExit("grid-copy SHA failure")
    subprocess.run([str(PY), str(E5D / "pest_eval.py"), "--pest", a.pest, "--years", str(a.year), "--skip", "dev"],
                   cwd=REPO, env=cell_env(os.environ, dst_root), check=True)
    metric = dst / "eval/clean_pooled_metrics.csv"
    if not metric.exists() or not (dst / "selector_artifacts_v2").exists(): raise SystemExit("missing selector output artifact")
    import pandas as pd
    value = float(pd.read_csv(metric).iloc[0].IoU80_overall_tol0)
    (dst / "cell_result.json").write_text(json.dumps({"arm": "T", "pest": a.pest, "year": a.year, "seed": a.seed,
        "iou80_overall_tol0": value, "feature_mu_position": True, "copied_inputs": copied}, indent=2) + "\n")
    return 0


def selftest():
    # the canonical WBPH runner's env literal + its T-only mu_position switch == T_ENV
    src = CANON_RUNNER.read_text()
    tree = ast.parse(src)
    canon = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "update" and n.args and isinstance(n.args[0], ast.Dict):
            for k, v in zip(n.args[0].keys, n.args[0].values):
                if isinstance(k, ast.Constant) and isinstance(v, ast.Constant): canon[k.value] = v.value
    assert 'if a.arm == "T": env["WBPH_SELECTOR_ADD_MU_POSITION"]="1"' in src
    canon["WBPH_SELECTOR_ADD_MU_POSITION"] = "1"
    assert canon == T_ENV, (canon, T_ENV)
    env = cell_env({"X": "1"}, Path("/tmp/r"))
    assert env["ALLPESTS_OUT_ROOT"] == env["OUT_ROOT"] == "/tmp/r" and env["X"] == "1"
    assert env["PYTHONPATH"] == f"{E5D / 'vendor'}:{REPO}"
    assert "WBPH" not in PESTS
    print("selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: selftest(); sys.exit(0)
    raise SystemExit(main())
