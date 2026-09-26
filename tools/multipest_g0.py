#!/usr/bin/env python3
"""G0 input gate for one crosspest pest (read-only).

Checks, all against the frozen manifests of the multi-pest freeze commit:
  dispatch + climatology  sha256 (manifests/multipest/STAGE1_DISPATCH.sha256), inside the repo
  raw data                daily table + this pest's label file (manifests/multipest/RAW_DATA.sha256)
                          under RICE_DATA_ROOT (default <repo>/data)
  15 B checkpoints        present inside the repo; pest, DOY window == rice/pests/<pest>/config.py,
                          window 90, Experiment-B history_gate.* weights, stored dispatch path
                          re-roots to this pest/year's frozen dispatch file, D28 frozen-norm
                          checkpoint present and sha256 == frozen_norm_source.sha256, splits present
Release-asset sha256 lists are checked separately with `sha256sum -c` by the acceptance launcher.

usage: multipest_g0.py PEST [--out g0.json]      (from any cwd; PYTHONPATH=<repo>)
exit 0 only if every check passes.
"""
import argparse, importlib, json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "tools"))
from pest_grid_reroot import sha, to_repo, reroot   # noqa: E402

PESTS = ("sheath_blight", "bacterial_blight", "brown_spot", "rice_stem_borer_1",
         "rice_stem_borer_2", "BPH", "blast")
XR = "rice/outputs_crosspest_frozen_replication_20260818"
BATCH = {2022: "batch_2022_baseline", 2023: "batch_2023_baseline", 2024: "batch_2024_bestgate"}
MP = REPO / "manifests/multipest"


def lines(p): return [l.split(None, 1) for l in Path(p).read_text().splitlines() if l.strip()]


def run(pest, repo=REPO):
    checks = []

    def check(name, fn):
        try: detail = fn(); checks.append({"check": name, "pass": True, "detail": detail})
        except (SystemExit, Exception) as e: checks.append({"check": name, "pass": False, "detail": f"{type(e).__name__}: {e}"})

    def file_sha(rel, want):
        p = to_repo(rel, repo)
        got = sha(p)
        if got != want: raise SystemExit(f"sha256 {got} != {want}")
        return rel

    disp = [(h, r) for h, r in lines(MP / "STAGE1_DISPATCH.sha256") if f"/{pest}/" in r]
    if len(disp) != 6: checks.append({"check": "dispatch manifest rows", "pass": False, "detail": f"{len(disp)} != 6"})
    for h, r in disp: check(f"dispatch/clim {r}", lambda r=r, h=h: file_sha(r, h))

    cfg = importlib.import_module(f"rice.pests.{pest}.config")
    data_root = Path(os.environ.get("RICE_DATA_ROOT", repo / "data"))
    label_rel = f"rice/LONG_by_pest/{Path(cfg.PATH_OBS).name}"
    raw = dict((r, h) for h, r in lines(MP / "RAW_DATA.sha256"))
    daily_rel = next(r for r in raw if r.startswith("rice/") and "LONG_by_pest" not in r)
    for rel in (daily_rel, label_rel):
        def raw_check(rel=rel):
            if rel not in raw: raise SystemExit("not in RAW_DATA.sha256")
            got = sha(data_root / rel)
            if got != raw[rel]: raise SystemExit(f"sha256 {got} != {raw[rel]}")
            return str(data_root / rel)
        check(f"raw {rel}", raw_check)

    import torch
    for y in BATCH:
        want_disp = {r.strip() for _, r in disp if f"/{BATCH[y]}/" in r and "/gate_" in r}
        for s in range(5):
            cell = f"{XR}/B/{y}/seed{s}/{pest}/clean"

            def ck_check(y=y, s=s, cell=cell, want_disp=want_disp):
                ck = torch.load(to_repo(f"{cell}/ckpt/{y}/ckpt/checkpoint_run4.pt", repo), map_location="cpu", weights_only=False)
                bad = []
                if ck.get("pest") != pest: bad.append(f"pest {ck.get('pest')}")
                if (int(ck["doy_start"]), int(ck["doy_end"])) != (cfg.DOY_START, cfg.DOY_END): bad.append(f"doy {ck['doy_start']}-{ck['doy_end']}")
                if int(ck.get("stage2_nowcast_window", -1)) != 90: bad.append("window != 90")
                if not any(k.startswith("history_gate.") for k in ck["trained_states"][0]["state_dict"]): bad.append("no history_gate")
                d = Path(reroot(ck["stage2_dispatch_feature_csv"], repo)).relative_to(Path(repo).resolve()).as_posix()
                if {d} != want_disp: bad.append(f"dispatch {d} not frozen file for {y}")
                fn = ck["frozen_norm_source"]
                d28 = to_repo(f"{XR}/D28/{y}/seed{s}/{pest}/clean/ckpt/{y}/ckpt/checkpoint_run4.pt", repo)
                if sha(d28) != fn["sha256"]: bad.append("D28 sha != frozen_norm_source")
                for f in ("split_assignment.json", "split_manifest.csv", "split_overlap_checks.json"): to_repo(f"{cell}/{f}", repo)
                if bad: raise SystemExit("; ".join(bad))
                return "ok"
            check(f"checkpoint {y}/seed{s}", ck_check)
    return {"pest": pest, "gate": "G0", "pass": all(c["pass"] for c in checks), "n_checks": len(checks),
            "n_failed": sum(not c["pass"] for c in checks), "checks": checks}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("pest", choices=PESTS); ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    res = run(a.pest)
    txt = json.dumps(res, indent=1)
    if a.out: a.out.parent.mkdir(parents=True, exist_ok=True); a.out.write_text(txt + "\n")
    print(json.dumps({k: res[k] for k in ("pest", "gate", "pass", "n_checks", "n_failed")}))
    for c in res["checks"]:
        if not c["pass"]: print(f"FAIL {c['check']}: {c['detail']}", file=sys.stderr)
    sys.exit(0 if res["pass"] else 1)
