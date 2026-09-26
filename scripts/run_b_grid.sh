#!/usr/bin/env bash
# Regenerate the 15 canonical B offset grids (WBPH, eval years 2022-2024 x Stage-2 seeds 0-4)
# from the B checkpoints. Same command and environment as the verified run (G1 15/15 bitwise).
#   B_ROOT  default: $REPO_ROOT/rice/outputs_allpests_e5d_expB_20260817 (release asset layout)
#   --check compare the regenerated grids with manifests/B_GRID_SHA256.txt (G1 gate)
set -euo pipefail
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
b_root="${B_ROOT:-$repo/rice/outputs_allpests_e5d_expB_20260817}"
cd "$repo"
unset CROPSCIENCE_ROOT WBPH_WS_ROOT RICE_DAILY_CSV RICE_LONG_BY_PEST_DIR WANDB_PROJECT WANDB_ENTITY
export PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled WBPH_EXPB_HISTORY_GATE=1 MPLBACKEND=Agg
source "$repo/rice/experiments/allpests_e5d/common.sh"
export_e5d_env
mkdir -p "$repo/logs"
for y in 2022 2023 2024; do for s in 0 1 2 3 4; do
  export ALLPESTS_OUT_ROOT="$b_root/$y/seed$s" OUT_ROOT="$b_root/$y/seed$s"
  g="$ALLPESTS_OUT_ROOT/WBPH/clean/grid/WBPH_E5d_clean_grid_1to75.csv"
  [[ -f "$ALLPESTS_OUT_ROOT/WBPH/clean/ckpt/$y/ckpt/checkpoint_run4.pt" ]] || { echo "[abort] missing B checkpoint for $y seed$s" >&2; exit 4; }
  [[ ! -e "$g" ]] || { echo "[abort] grid already exists (remove it to regenerate): $g" >&2; exit 3; }
  echo "[grid] $y seed$s $(date -Is)"
  PYTHONPATH="$VENDOR:$CS" "$PY" "$repo/rice/experiments/allpests_e5d/pest_grid.py" --pest WBPH --mode clean --years "$y" --force > "$repo/logs/grid_${y}_seed${s}.log" 2>&1
  [[ -s "$g" ]] || { echo "[abort] grid not written: $g" >&2; exit 5; }
done; done
if [[ "${1:-}" == --check ]]; then
  (cd "$b_root" && sha256sum -c "$repo/manifests/B_GRID_SHA256.txt")
fi
