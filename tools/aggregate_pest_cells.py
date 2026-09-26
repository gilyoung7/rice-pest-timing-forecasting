#!/usr/bin/env python3
"""Deterministic 15-cell selector-T aggregate + anchor gate for one crosspest pest.

Same rules as tools/aggregate_selector_cells.py (WBPH, unchanged): exactly the 15 cells,
cell_result.json == clean_pooled_metrics.csv within 1e-12, macro = math.fsum / 15, and with
--anchor every cell (G2) and the macro (G3) within 1e-12. Additionally the anchor itself is
schema-checked (pest, 15 unique cells, macro == fsum of its cells).

usage: aggregate_pest_cells.py PEST RUNS_DIR OUT_DIR [--anchor audit/multipest/<pest>/canonical_anchor.json]
       aggregate_pest_cells.py --selftest
Exit 0 only if every check (and the anchor gate, when given) passes.
"""
import csv, hashlib, json, math, sys, tempfile
from pathlib import Path

YEARS, SEEDS, TOL, ARM = (2022, 2023, 2024), range(5), 1e-12, "T"
CELLS = [(y, s) for y in YEARS for s in SEEDS]


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_anchor(a, pest):
    if a.get("pest") != pest: raise SystemExit(f"FAIL anchor pest {a.get('pest')!r} != {pest!r}")
    keys = [(c["year"], c["seed"]) for c in a["cells"]]
    if sorted(keys) != sorted(CELLS) or len(set(keys)) != 15: raise SystemExit("FAIL anchor needs exactly the 15 cells")
    if abs(math.fsum(c["value"] for c in a["cells"]) / 15 - a["macro"]) > TOL: raise SystemExit("FAIL anchor macro != fsum of its cells")


def aggregate(pest, runs, out, anchor=None):
    runs, out = Path(runs), Path(out)
    found = sorted(runs.glob(f"{ARM}/*/seed*/{pest}/cell_result.json"))
    want = [runs / ARM / str(y) / f"seed{s}" / pest / "cell_result.json" for y, s in CELLS]
    if sorted(found) != sorted(want): raise SystemExit(f"FAIL need exactly the 15 cells, found {len(found)}")
    rows, inputs, pooled_d = [], {}, []
    for (y, s), p in zip(CELLS, want):
        d = json.loads(p.read_text()); v = d["iou80_overall_tol0"]
        if (d["arm"], d.get("pest"), d["year"], d["seed"]) != (ARM, pest, y, s): raise SystemExit(f"FAIL path/content mismatch {p}")
        if not (isinstance(v, float) and math.isfinite(v)): raise SystemExit(f"FAIL non-finite {p}")
        if d.get("feature_mu_position") is not True: raise SystemExit(f"FAIL mu_position not on {p}")
        m = p.parent / "eval/clean_pooled_metrics.csv"
        pooled = list(csv.DictReader(m.open()))
        dp = float(pooled[0]["IoU80_overall_tol0"]) - v if len(pooled) == 1 else math.inf
        if abs(dp) > TOL: raise SystemExit(f"FAIL pooled metric mismatch {m} delta={dp}")
        pooled_d.append(abs(dp)); rows.append((ARM, y, s, v)); inputs[str(p)] = sha(p); inputs[str(m)] = sha(m)
    macro = math.fsum(r[3] for r in rows) / 15
    out.mkdir(parents=True, exist_ok=True)
    with (out / "cells.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["pest", "arm", "year", "seed", "iou80_overall_tol0"])
        w.writerows((pest, a, y, s, repr(v)) for a, y, s, v in rows)
    res = {"pest": pest, "arm": ARM, "n_cells": 15, "macro_iou80_overall_tol0": macro, "inputs_sha256": inputs,
           "aggregator_sha256": sha(__file__), "anchor_gate": None, "max_abs_pooled_csv_delta": max(pooled_d)}
    if anchor:
        a = json.loads(Path(anchor).read_text()); check_anchor(a, pest)
        ref = {(c["year"], c["seed"]): c["value"] for c in a["cells"]}
        cell_d = {f"{y}/{s}": v - ref[(y, s)] for _, y, s, v in rows}
        bad = {k: d for k, d in cell_d.items() if abs(d) > TOL}
        g2, g3 = not bad, abs(macro - a["macro"]) <= TOL
        res["anchor_gate"] = {"anchor_sha256": sha(anchor), "tol": TOL, "cells_pass": 15 - len(bad),
                              "max_abs_cell_delta": max(abs(d) for d in cell_d.values()), "failed_cells": bad,
                              "anchor_macro": a["macro"], "macro_delta": macro - a["macro"],
                              "G2_pass": g2, "G3_pass": g3, "pass": g2 and g3}
    (out / "aggregate.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print(json.dumps({k: res[k] for k in ("pest", "n_cells", "macro_iou80_overall_tol0", "anchor_gate")}, indent=1))
    if anchor and not res["anchor_gate"]["pass"]: raise SystemExit("FAIL anchor gate")
    return res


def selftest():
    def expect(fn, msg):
        try: fn(); raise AssertionError(f"should fail: {msg}")
        except SystemExit as e: assert msg in str(e), (msg, e)
    with tempfile.TemporaryDirectory() as t:
        t, pest = Path(t), "blast"; cells = []
        for y, s in CELLS:
            v = 0.4 + 0.01 * s + 0.001 * (y - 2022); cells.append({"year": y, "seed": s, "value": v})
            d = t / "runs/T" / str(y) / f"seed{s}" / pest; (d / "eval").mkdir(parents=True)
            (d / "cell_result.json").write_text(json.dumps({"arm": "T", "pest": pest, "year": y, "seed": s, "iou80_overall_tol0": v, "feature_mu_position": True}))
            (d / "eval/clean_pooled_metrics.csv").write_text(f"IoU80_overall_tol0\n{v!r}\n")
        macro = math.fsum(c["value"] for c in cells) / 15
        def anc(**k):
            (t / "a.json").write_text(json.dumps({"pest": pest, "cells": cells, "macro": macro, **k})); return t / "a.json"
        r = aggregate(pest, t / "runs", t / "o1", anc())
        assert r["anchor_gate"]["pass"] and r["anchor_gate"]["cells_pass"] == 15 and r["macro_iou80_overall_tol0"] == macro
        expect(lambda: aggregate(pest, t / "runs", t / "o2", anc(pest="BPH")), "anchor pest")
        expect(lambda: aggregate(pest, t / "runs", t / "o3", anc(macro=macro + 1e-9)), "anchor macro != fsum")
        cells[0]["value"] += 1e-9
        expect(lambda: aggregate(pest, t / "runs", t / "o4", anc(macro=math.fsum(c["value"] for c in cells) / 15)), "anchor gate")
        cells.pop()
        expect(lambda: aggregate(pest, t / "runs", t / "o5", anc(macro=math.fsum(c["value"] for c in cells) / 15)), "exactly the 15 cells")
        expect(lambda: aggregate("BPH", t / "runs", t / "o6"), "exactly the 15 cells")
        (t / "runs/T/2024/seed4" / pest / "cell_result.json").unlink()
        expect(lambda: aggregate(pest, t / "runs", t / "o7"), "exactly the 15 cells")
    print("selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: selftest(); sys.exit(0)
    args = sys.argv[1:]; anchor = None
    if "--anchor" in args: i = args.index("--anchor"); anchor = args[i + 1]; del args[i:i + 2]
    if len(args) != 3: raise SystemExit(__doc__)
    aggregate(*args, anchor=anchor)
