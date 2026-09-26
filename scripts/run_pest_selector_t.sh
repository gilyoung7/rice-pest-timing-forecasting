#!/usr/bin/env bash
# Selector T (official_v1 + mu_position) for the 15 B cells of one pest, then the 15-cell aggregate.
#   run_pest_selector_t.sh WBPH [--anchor]   -> exactly scripts/run_selector_t.sh (canonical WBPH path, unchanged)
#   run_pest_selector_t.sh <crosspest pest> [--anchor]
#       cells via tools/run_pest_selector_cell.py -> outputs/multipest/<pest>/selector_T/runs/T/
#       aggregate via tools/aggregate_pest_cells.py -> outputs/multipest/<pest>/selector_T_aggregate/
#       --anchor gates every cell (G2) and the macro (G3) against audit/multipest/<pest>/canonical_anchor.json
# Needs the grids produced by scripts/run_pest_b_grid.sh <pest>.
set -euo pipefail
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
pest="${1:?usage: run_pest_selector_t.sh <pest> [--anchor]}"; shift
if [[ "$pest" == WBPH ]]; then exec "$repo/scripts/run_selector_t.sh" "$@"; fi
case "$pest" in sheath_blight|bacterial_blight|brown_spot|rice_stem_borer_1|rice_stem_borer_2|BPH|blast) ;;
  *) echo "[abort] unknown pest: $pest" >&2; exit 64 ;; esac
cd "$repo"
unset CROPSCIENCE_ROOT WBPH_WS_ROOT RICE_DAILY_CSV RICE_LONG_BY_PEST_DIR WANDB_PROJECT WANDB_ENTITY WBPH_SELECTOR_ADD_MU_POSITION
export PYTHONDONTWRITEBYTECODE=1 WANDB_MODE=disabled MPLBACKEND=Agg
anchor=(); [[ "${1:-}" == --anchor ]] && anchor=(--anchor "$repo/audit/multipest/$pest/canonical_anchor.json")
base="$repo/outputs/multipest/$pest"; runs="$base/selector_T/runs"
[[ ! -e "$runs/T" ]] || { echo "[abort] $runs/T already exists" >&2; exit 3; }
logs="$repo/logs/multipest/$pest"; mkdir -p "$logs"
for y in 2022 2023 2024; do for s in 0 1 2 3 4; do
  echo "[T] $pest $y seed$s $(date -Is)"
  "$repo/.venv/bin/python" -u tools/run_pest_selector_cell.py --pest "$pest" --year "$y" --seed "$s" --runs-root "$runs" > "$logs/selector_T_${y}_seed${s}.log" 2>&1
  [[ -s "$runs/T/$y/seed$s/$pest/cell_result.json" ]] || { echo "[abort] no cell_result for $pest $y seed$s" >&2; exit 5; }
done; done
"$repo/.venv/bin/python" tools/aggregate_pest_cells.py "$pest" "$runs" "$base/selector_T_aggregate" "${anchor[@]}"
