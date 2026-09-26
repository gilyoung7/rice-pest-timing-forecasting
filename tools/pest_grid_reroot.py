#!/usr/bin/env python3
"""pest_grid.py for the seven crosspest pests, with the checkpoint dispatch path re-rooted.

The crosspest B checkpoints store `stage2_dispatch_feature_csv` as an absolute path of the
original server, and the grid code reads that path from the checkpoint. This wrapper leaves the
checkpoints and the grid code untouched: it wraps `load_dispatch_feature_table` so the stored path
is mapped into this repository, must resolve (symlinks followed) inside it, and must match
manifests/multipest/STAGE1_DISPATCH.sha256. Anything else aborts; nothing falls back to the
original tree. WBPH does not use this file (scripts/run_b_grid.sh).

usage: pest_grid_reroot.py <pest_grid.py args>      (run from the repo root, PYTHONPATH=$VENDOR:$REPO)
       pest_grid_reroot.py --selftest
"""
import hashlib, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ORIG_PREFIX = "/home/gpu4080/research/cropscience_multipest/"   # crosspest server checkout
MANIFEST = REPO / "manifests/multipest/STAGE1_DISPATCH.sha256"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def to_repo(stored, repo=REPO):
    """Map a stored original-server path (or a repo-relative path) to an existing file inside repo."""
    s = str(stored)
    rel = s[len(ORIG_PREFIX):] if s.startswith(ORIG_PREFIX) else s
    if Path(rel).is_absolute():
        raise SystemExit(f"[reroot] FAIL absolute path outside the known prefix: {s}")
    root = Path(repo).resolve()
    p = (root / rel).resolve()
    if not p.is_relative_to(root):
        raise SystemExit(f"[reroot] FAIL resolves outside the repository: {s} -> {p}")
    if not p.is_file():
        raise SystemExit(f"[reroot] FAIL missing in repository: {p}")
    return p


def reroot(stored, repo=REPO, manifest=MANIFEST):
    root = Path(repo).resolve(); p = to_repo(stored, repo)
    want = {l.split()[1]: l.split()[0] for l in Path(manifest).read_text().splitlines() if l.strip()}
    key = p.relative_to(root).as_posix()
    if key not in want:
        raise SystemExit(f"[reroot] FAIL not a frozen dispatch file: {key}")
    if sha(p) != want[key]:
        raise SystemExit(f"[reroot] FAIL sha256 mismatch: {key}")
    return str(p)


def main():
    ap_dir = REPO / "rice/experiments/allpests_e5d"
    sys.path.insert(0, str(ap_dir))
    sys.argv = [str(ap_dir / "pest_grid.py")] + sys.argv[1:]
    import pest_grid                                     # loads 87 as pest_grid.mk87
    import rice.scripts.stage1_confidence_utils as U     # eval_s2n_direct_compare imports from here at call time
    orig = U.load_dispatch_feature_table
    seen = set()

    def patched(csv_path, *a, **k):
        p = reroot(csv_path)
        if p not in seen: seen.add(p); print(f"[reroot] {csv_path} -> {p}", flush=True)
        return orig(p, *a, **k)

    U.load_dispatch_feature_table = patched
    pest_grid.mk87.load_dispatch_feature_table = patched  # bound at 87 import time
    pest_grid.main()
    if not seen: raise SystemExit("[reroot] FAIL no dispatch table was loaded")


def selftest():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); repo, outside = t / "repo", t / "outside"
        d = repo / "rice/outputs/stage2/batch_2022_baseline/BPH"; d.mkdir(parents=True); outside.mkdir()
        f = d / "gate_A_R088_features_per_sy.csv"; f.write_text("site,year\n")
        (outside / "x.csv").write_text("site,year\n")
        rel = f.relative_to(repo).as_posix()
        m = t / "m.sha256"; m.write_text(f"{sha(f)}  {rel}\n")
        assert reroot(ORIG_PREFIX + rel, repo, m) == str(f.resolve())            # original absolute
        assert reroot(rel, repo, m) == str(f.resolve())                          # repo-relative
        (repo / "rice/outputs/stage2/link").symlink_to(outside)
        bad = [("/etc/passwd", "outside the known prefix"),
               (str(outside / "x.csv"), "outside the known prefix"),
               (ORIG_PREFIX + "../../x.csv", "outside the repository"),
               ("rice/outputs/stage2/link/x.csv", "outside the repository"),   # symlink escape
               (ORIG_PREFIX + "rice/outputs/stage2/nope.csv", "missing"),
               ]
        for s, msg in bad:
            try: reroot(s, repo, m); raise AssertionError(f"accepted {s}")
            except SystemExit as e: assert msg in str(e), (s, e)
        g = d / "gate_B_R088_features_per_sy.csv"; g.write_text("x\n")
        try: reroot(ORIG_PREFIX + g.relative_to(repo).as_posix(), repo, m); raise AssertionError("unlisted")
        except SystemExit as e: assert "not a frozen dispatch" in str(e)
        f.write_text("site,year\nchanged\n")
        try: reroot(rel, repo, m); raise AssertionError("sha")
        except SystemExit as e: assert "sha256 mismatch" in str(e)
    print("selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: selftest(); sys.exit(0)
    main()
