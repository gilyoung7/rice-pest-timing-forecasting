#!/usr/bin/env bash
# Canonical selector T (selector v2 = official_v1 + mu_position) for the 15 B cells, then a
# deterministic aggregate. Replaces the original run_selround1.sh / finalize_selround1.py; the
# per-cell computation is the unchanged audit/selround1_20260818/run_selector_cell.py.
# Inputs: B grids + splits under rice/outputs_allpests_e5d_expB_20260817 (run scripts/run_b_grid.sh
# first). Outputs: audit/selround1_20260818/runs/T/ and outputs/selector_T_aggregate/.
#   --anchor   also gate every cell and the macro against audit/canonical_anchor.json (<=1e-12)
set -euo pipefail
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$repo"
unset CROPSCIENCE_ROOT WBPH_WS_ROOT RICE_DAILY_CSV RICE_LONG_BY_PEST_DIR WANDB_PROJECT WANDB_ENTITY WBPH_SELECTOR_ADD_MU_POSITION
export PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled MPLBACKEND=Agg
anchor=(); [[ "${1:-}" == --anchor ]] && anchor=(--anchor "$repo/audit/canonical_anchor.json")
runs="$repo/audit/selround1_20260818/runs"
[[ ! -e "$runs/T" ]] || { echo "[abort] $runs/T already exists" >&2; exit 3; }
mkdir -p "$repo/logs"
for y in 2022 2023 2024; do for s in 0 1 2 3 4; do
  echo "[T] $y seed$s $(date -Is)"
  "$repo/.venv/bin/python" -u audit/selround1_20260818/run_selector_cell.py --arm T --year "$y" --seed "$s" > "$repo/logs/selector_T_${y}_seed${s}.log" 2>&1
  [[ -s "$runs/T/$y/seed$s/WBPH/cell_result.json" ]] || { echo "[abort] no cell_result for $y seed$s" >&2; exit 5; }
done; done
"$repo/.venv/bin/python" tools/aggregate_selector_cells.py "$runs" T "$repo/outputs/selector_T_aggregate" "${anchor[@]}"
