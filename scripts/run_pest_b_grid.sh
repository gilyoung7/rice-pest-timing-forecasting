#!/usr/bin/env bash
# Regenerate the 15 B offset grids of one pest.
#   run_pest_b_grid.sh WBPH [--check]   -> exactly scripts/run_b_grid.sh (canonical WBPH path, unchanged)
#   run_pest_b_grid.sh <crosspest pest> [--check]
#       grids from rice/outputs_crosspest_frozen_replication_20260818/B (B_ROOT) via
#       tools/pest_grid_reroot.py (checkpoint dispatch path re-rooted into this repo);
#       --check compares with manifests/multipest/B_GRID_SHA256_<pest>.txt (G1 gate)
set -euo pipefail
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
pest="${1:?usage: run_pest_b_grid.sh <pest> [--check]}"; shift
if [[ "$pest" == WBPH ]]; then exec "$repo/scripts/run_b_grid.sh" "$@"; fi
case "$pest" in sheath_blight|bacterial_blight|brown_spot|rice_stem_borer_1|rice_stem_borer_2|BPH|blast) ;;
  *) echo "[abort] unknown pest: $pest" >&2; exit 64 ;; esac
b_root="${B_ROOT:-$repo/rice/outputs_crosspest_frozen_replication_20260818/B}"
cd "$repo"
unset CROPSCIENCE_ROOT WBPH_WS_ROOT RICE_DAILY_CSV RICE_LONG_BY_PEST_DIR WANDB_PROJECT WANDB_ENTITY
export PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled WBPH_EXPB_HISTORY_GATE=1 MPLBACKEND=Agg
source "$repo/rice/experiments/allpests_e5d/common.sh"
export_e5d_env
logs="$repo/logs/multipest/$pest"; mkdir -p "$logs"
for y in 2022 2023 2024; do for s in 0 1 2 3 4; do
  export ALLPESTS_OUT_ROOT="$b_root/$y/seed$s" OUT_ROOT="$b_root/$y/seed$s"
  g="$ALLPESTS_OUT_ROOT/$pest/clean/grid/${pest}_E5d_clean_grid_1to75.csv"
  [[ -f "$ALLPESTS_OUT_ROOT/$pest/clean/ckpt/$y/ckpt/checkpoint_run4.pt" ]] || { echo "[abort] missing B checkpoint for $pest $y seed$s" >&2; exit 4; }
  [[ ! -e "$g" ]] || { echo "[abort] grid already exists (remove it to regenerate): $g" >&2; exit 3; }
  echo "[grid] $pest $y seed$s $(date -Is)"
  PYTHONPATH="$VENDOR:$CS" "$PY" "$repo/tools/pest_grid_reroot.py" --pest "$pest" --mode clean --years "$y" --force > "$logs/grid_${y}_seed${s}.log" 2>&1
  [[ -s "$g" ]] || { echo "[abort] grid not written: $g" >&2; exit 5; }
done; done
if [[ "${1:-}" == --check ]]; then
  (cd "$b_root" && sha256sum -c "$repo/manifests/multipest/B_GRID_SHA256_${pest}.txt")
fi
