#!/usr/bin/env python
"""Code provenance manifest for the training and grid processes.

One helper, called once per process and reused at every checkpoint save site, so the fields are
never re-typed per save location. Records where each executing module actually came from, not
where it is nominally expected to be.
"""
from __future__ import annotations
import hashlib, importlib, platform, subprocess, sys
from pathlib import Path

# Cross-process equality is required only for the sources that define what the model computes.
# run_train is never loaded by the grid process, so it is recorded but never asserted.
CROSS_PROCESS_REQUIRED = ("model",)
DEFAULT_MODULES = ("src.vendor.model", "src.vendor.run_train", "rice.src.train_eval")


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _git(path: Path, *args) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(path.parent), *args],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:                                                     # noqa: BLE001
        return None


def _repo_rel(p: Path) -> str | None:
    top = _git(p, "rev-parse", "--show-toplevel")
    if not top:
        return None
    try:
        return str(p.relative_to(Path(top)))
    except ValueError:
        return None


def _ver(name: str) -> str | None:
    try:
        return importlib.import_module(name).__version__
    except Exception:                                                     # noqa: BLE001
        return None


def module_record(name: str) -> dict:
    m = sys.modules.get(name)
    if m is None:
        m = importlib.import_module(name)
    p = Path(m.__file__)
    rp = p.resolve()
    return {"module": name, "file": str(p), "realpath": str(rp), "sha256": _sha256(rp),
            "repo_relative": _repo_rel(rp), "git_commit": _git(rp, "rev-parse", "HEAD"),
            "git_dirty": bool(_git(rp, "status", "--porcelain") or "") or None}


def build_code_manifest(modules=DEFAULT_MODULES, extra: dict | None = None) -> dict:
    import torch
    out = {}
    for name in modules:
        try:
            out[name.rsplit(".", 1)[-1]] = module_record(name)
        except Exception as e:                                            # noqa: BLE001
            out[name.rsplit(".", 1)[-1]] = {"module": name, "error": f"{type(e).__name__}: {e}"}
    out["environment"] = {
        "python": platform.python_version(), "torch": torch.__version__,
        "cuda": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
        "lightgbm": _ver("lightgbm"), "numpy": _ver("numpy"), "pandas": _ver("pandas"),
        "sklearn": _ver("sklearn"),
        "deterministic_algorithms": bool(torch.are_deterministic_algorithms_enabled()),
        "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
        "cudnn_benchmark": bool(torch.backends.cudnn.benchmark)}
    if extra:
        out.update(extra)
    return out


def assert_cross_process(train_provenance, grid_manifest, keys=CROSS_PROCESS_REQUIRED):
    """Compare a checkpoint's recorded training manifest against this process's manifest.

    Checkpoints written before this helper existed carry nothing; they are reported as
    'unrecorded' and allowed through. They are never reported as 'verified same source'.
    """
    if not train_provenance:
        print("[provenance] checkpoint code_provenance = unrecorded "
              "(cannot be asserted same-source)", flush=True)
        return "unrecorded"
    bad = []
    for k in keys:
        a = (train_provenance.get(k) or {}).get("sha256")
        b = (grid_manifest.get(k) or {}).get("sha256")
        if a is None or b is None or a != b:
            bad.append((k, a, b))
    if bad:
        lines = "\n".join(f"    {k}: train={a} grid={b}" for k, a, b in bad)
        raise SystemExit(f"[abort] CODE PROVENANCE MISMATCH\n{lines}")
    print("[provenance] cross-process match on " + ", ".join(keys), flush=True)
    return "verified"


def save_runtime_manifest(path, manifest, side, cross_result=None, resolved_inputs=None,
                          extra=None):
    """Write the process's own manifest to disk. The checkpoint carries the TRAINING manifest;
    this is the grid/eval counterpart, which previously existed only in stdout."""
    import json as _json, os as _os, tempfile as _tf
    rec = {"side": side, "manifest": manifest, "cross_process_result": cross_result,
           "resolved_input_paths": resolved_inputs or {},
           "data_path_env_verified_unset":
               _json.loads(_os.environ.get("E5D_DATA_PATH_ENV_UNSET", "{}")),
           "historical_note": (
               "Checkpoints written before code_provenance existed carry 'unrecorded'. "
               "An infra parity gate demonstrating numerical continuity is NOT a claim that a "
               "historical checkpoint was produced by the same source; that is not asserted.")}
    if extra:
        rec.update(extra)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = _tf.mkstemp(dir=str(path.parent), suffix=".tmp"); _os.close(fd)
    Path(tmp).write_text(_json.dumps(rec, indent=1, default=str))
    _os.replace(tmp, path)
    return path
