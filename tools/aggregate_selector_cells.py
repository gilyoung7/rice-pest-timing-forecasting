#!/usr/bin/env python3
"""Deterministic 15-cell aggregate of selector cell_result.json (replaces finalize_selround1.py).

usage: aggregate_selector_cells.py RUNS_DIR ARM OUT_DIR [--anchor canonical_anchor.json]
       aggregate_selector_cells.py --selftest
Exit 0 only if every check (and the anchor gate, when given) passes.
"""
import csv, hashlib, json, math, sys, tempfile
from pathlib import Path

YEARS, SEEDS, TOL = (2022, 2023, 2024), range(5), 1e-12

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def aggregate(runs, arm, out, anchor=None):
    runs, out = Path(runs), Path(out)
    found = sorted(runs.glob(f"{arm}/*/seed*/WBPH/cell_result.json"))
    want = [runs / arm / str(y) / f"seed{s}" / "WBPH" / "cell_result.json" for y in YEARS for s in SEEDS]
    if sorted(found) != sorted(want): raise SystemExit(f"FAIL need exactly the 15 cells, found {len(found)}")
    rows, inputs, pooled_d = [], {}, []
    for (y, s), p in zip([(y, s) for y in YEARS for s in SEEDS], want):
        d = json.loads(p.read_text()); v = d["iou80_overall_tol0"]
        if (d["arm"], d["year"], d["seed"]) != (arm, y, s): raise SystemExit(f"FAIL path/content mismatch {p}")
        if not (isinstance(v, float) and math.isfinite(v)): raise SystemExit(f"FAIL non-finite {p}")
        if arm == "T" and d.get("feature_mu_position") is not True: raise SystemExit(f"FAIL mu_position not on {p}")
        m = p.parent / "eval/clean_pooled_metrics.csv"
        pooled = list(csv.DictReader(m.open()))
        # cell_result.json holds pandas' parse of this CSV, which can differ from float() by 1 ulp
        dp = float(pooled[0]["IoU80_overall_tol0"]) - v if len(pooled) == 1 else math.inf
        if abs(dp) > TOL: raise SystemExit(f"FAIL pooled metric mismatch {m} delta={dp}")
        pooled_d.append(abs(dp)); rows.append((arm, y, s, v)); inputs[str(p)] = sha(p); inputs[str(m)] = sha(m)
    macro = math.fsum(r[3] for r in rows) / 15
    out.mkdir(parents=True, exist_ok=True)
    with (out / "cells.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["arm", "year", "seed", "iou80_overall_tol0"])
        w.writerows((a, y, s, repr(v)) for a, y, s, v in rows)
    res = {"arm": arm, "n_cells": 15, "macro_iou80_overall_tol0": macro, "inputs_sha256": inputs,
           "aggregator_sha256": sha(__file__), "anchor_gate": None,
           "max_abs_pooled_csv_delta": max(pooled_d)}
    if anchor:
        a = json.loads(Path(anchor).read_text())
        ref = {(c["year"], c["seed"]): c["value"] for c in a["cells"]}
        cell_d = {f"{y}/{s}": v - ref[(y, s)] for _, y, s, v in rows}
        bad = {k: d for k, d in cell_d.items() if abs(d) > TOL}
        res["anchor_gate"] = {"anchor_sha256": sha(anchor), "tol": TOL, "cells_pass": 15 - len(bad),
                              "max_abs_cell_delta": max(abs(d) for d in cell_d.values()), "failed_cells": bad,
                              "anchor_macro": a["macro"], "macro_delta": macro - a["macro"],
                              "pass": not bad and abs(macro - a["macro"]) <= TOL}
    (out / "aggregate.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print(json.dumps({k: res[k] for k in ("n_cells", "macro_iou80_overall_tol0", "anchor_gate")}, indent=1))
    if anchor and not res["anchor_gate"]["pass"]: raise SystemExit("FAIL anchor gate")
    return res

def selftest():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); cells = []
        for y in YEARS:
            for s in SEEDS:
                v = 0.4 + 0.01 * s + 0.001 * (y - 2022); cells.append({"year": y, "seed": s, "value": v})
                d = t / "runs/T" / str(y) / f"seed{s}/WBPH"; (d / "eval").mkdir(parents=True)
                (d / "cell_result.json").write_text(json.dumps({"arm": "T", "year": y, "seed": s, "iou80_overall_tol0": v, "feature_mu_position": True}))
                (d / "eval/clean_pooled_metrics.csv").write_text(f"IoU80_overall_tol0\n{v!r}\n")
        macro = math.fsum(c["value"] for c in cells) / 15
        (t / "anchor.json").write_text(json.dumps({"cells": cells, "macro": macro}))
        assert aggregate(t / "runs", "T", t / "out", t / "anchor.json")["anchor_gate"]["pass"]
        cells[0]["value"] += 1e-9; (t / "anchor.json").write_text(json.dumps({"cells": cells, "macro": macro}))
        try: aggregate(t / "runs", "T", t / "out2", t / "anchor.json"); raise AssertionError("gate should fail")
        except SystemExit as e: assert "anchor gate" in str(e)
        (t / "runs/T/2024/seed4/WBPH/cell_result.json").unlink()
        try: aggregate(t / "runs", "T", t / "out3"); raise AssertionError("count should fail")
        except SystemExit as e: assert "exactly the 15" in str(e)
    print("selftest OK")

if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: selftest(); sys.exit(0)
    args = sys.argv[1:]; anchor = None
    if "--anchor" in args: i = args.index("--anchor"); anchor = args[i + 1]; del args[i:i + 2]
    if len(args) != 3: raise SystemExit(__doc__)
    aggregate(*args, anchor=anchor)
