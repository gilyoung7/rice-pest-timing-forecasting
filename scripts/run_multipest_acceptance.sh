#!/usr/bin/env bash
# Multi-pest clean-repo acceptance: per pest, G0 -> G1 -> G2/G3, each stage through
# scripts/tmux_terminal_wrapper.sh (terminal-state JSON + tmux wait-for signal). A failed stage
# stops only that pest's downstream stages; the other pests still run. Run inside tmux, from a
# fresh clone with release assets extracted and the data root in place.
#   run_multipest_acceptance.sh OUT_DIR [pest ...]      default pests: the seven crosspest pests
#   WBPH may be listed: G0 = sha256sum -c of its existing manifests, G1/G2/G3 = the canonical scripts.
# Writes OUT_DIR/<pest>/{G0,G1,G2G3}.{state.json,log}, OUT_DIR/summary.json. Never edits
# audit/CANONICAL_MULTIPEST.json (status changes are a separate, reviewed commit).
set -euo pipefail
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
out="$(realpath -m "${1:?usage: run_multipest_acceptance.sh OUT_DIR [pest ...]}")"; shift
pests=("$@"); ((${#pests[@]})) || pests=(sheath_blight bacterial_blight brown_spot rice_stem_borer_1 rice_stem_borer_2 BPH blast)
data="${RICE_DATA_ROOT:-$repo/data}"
run_id="$(date +%Y%m%dT%H%M%S)-$$"
cd "$repo"
mkdir -p "$out"

stage() {  # stage <pest> <name> <command...>
  local p="$1" n="$2"; shift 2
  "$repo/scripts/tmux_terminal_wrapper.sh" --stage "$p/$n" --state-file "$out/$p/$n.state.json" \
    --log-file "$out/$p/$n.log" --signal "mp-$run_id-$p-$n" -- "$@"
}

for p in "${pests[@]}"; do
  echo "[acceptance] $p $(date -Is)"
  if [[ "$p" == WBPH ]]; then
    g0=(bash -c "sha256sum -c manifests/RELEASE_ASSETS.sha256 && (cd '$data' && sha256sum -c '$repo/manifests/RAW_DATA.sha256')")
  else
    g0=(bash -c "PYTHONPATH='$repo' .venv/bin/python tools/multipest_g0.py '$p' --out '$out/$p/g0.json' && sha256sum -c 'manifests/multipest/RELEASE_ASSETS_$p.sha256'")
  fi
  stage "$p" G0 "${g0[@]}" || { echo "[acceptance] $p G0 FAILED" >&2; continue; }
  stage "$p" G1 scripts/run_pest_b_grid.sh "$p" --check || { echo "[acceptance] $p G1 FAILED" >&2; continue; }
  stage "$p" G2G3 scripts/run_pest_selector_t.sh "$p" --anchor || echo "[acceptance] $p G2/G3 FAILED" >&2
done

"$repo/.venv/bin/python" - "$repo" "$out" "${pests[@]}" <<'PY'
import json, sys
from pathlib import Path
repo, out, pests = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
summary = {}
for p in pests:
    st = {}
    for g in ("G0", "G1", "G2G3"):
        f = out / p / f"{g}.state.json"
        st[g] = json.loads(f.read_text())["status"] if f.exists() else "NOT_STARTED"
    agg = repo / ("outputs/selector_T_aggregate" if p == "WBPH" else f"outputs/multipest/{p}/selector_T_aggregate") / "aggregate.json"
    gate = json.loads(agg.read_text()).get("anchor_gate") if st["G2G3"] == "COMPLETED" and agg.exists() else None
    g2 = bool(gate) and gate["cells_pass"] == 15
    g3 = bool(gate) and abs(gate["macro_delta"]) <= gate["tol"]
    ok = st["G0"] == st["G1"] == "COMPLETED" and g2 and g3
    failed = next((g for g in ("G0", "G1", "G2G3") if st[g] != "COMPLETED"), None) or (None if ok else "G2G3")
    summary[p] = {"stages": st, "G2_cells_pass": gate and gate["cells_pass"], "G2_max_abs_cell_delta": gate and gate["max_abs_cell_delta"],
                  "G3_macro_delta": gate and gate["macro_delta"], "aggregate": str(agg) if gate else None,
                  "proposed_status": "ACCEPTED_HANDOFF_CANONICAL" if ok else "ACCEPTANCE_FAILED", "failed_stage": failed}
(out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
for p, s in summary.items(): print(f"{p:18s} {s['proposed_status']:27s} {s['stages']} failed={s['failed_stage']}")
sys.exit(0 if all(s["failed_stage"] is None for s in summary.values()) else 1)
PY
