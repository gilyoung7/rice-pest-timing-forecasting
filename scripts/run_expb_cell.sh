#!/usr/bin/env bash
# One preregistered Experiment-B cell: D90 protocol plus the approved history gate.
#
# Handoff change (paths only; training/grid/eval commands and arguments are unchanged):
#   REPO_ROOT      default: this repository
#   D90_ROOT       default: $REPO_ROOT/rice/outputs_allpests_e5d_d90_20260814   (release asset)
#   D28_ROOT       default: $REPO_ROOT/rice/outputs_allpests_e5d_asym5_max140_20260804 (release asset)
#   EXPB_OUT_ROOT  default: $REPO_ROOT/rice/outputs_expB_retrain  (never the canonical asset dir)
#   EXPB_DRY_RUN=1 print the resolved training arguments and exit before writing anything.
# The D90 train_args.txt records the frozen-norm D28 checkpoint as an absolute path on the
# original server. That file is provenance and is not edited; the path is re-rooted under
# $D28_ROOT at run time.
set -euo pipefail
year="${1:?usage: run_expb_cell.sh <eval_year> <seed>}"
seed="${2:?usage: run_expb_cell.sh <eval_year> <seed>}"
repo="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
e5d="$repo/rice/experiments/allpests_e5d"
d90_root="${D90_ROOT:-$repo/rice/outputs_allpests_e5d_d90_20260814}"
d28_root="${D28_ROOT:-$repo/rice/outputs_allpests_e5d_asym5_max140_20260804}"
out_root="${EXPB_OUT_ROOT:-$repo/rice/outputs_expB_retrain}"
source_root="$d90_root/$year/seed$seed/WBPH"
proot="$out_root/$year/seed$seed/WBPH"
out="$proot/clean/ckpt/$year"

[[ ! -e "$proot" ]] || { echo "[abort] refusing to overwrite Experiment-B output: $proot" >&2; exit 3; }
ref_args="$source_root/clean/ckpt/$year/train_args.txt"
assign="$source_root/clean/split_assignment.json"
[[ -f "$ref_args" && -f "$assign" ]] || { echo "[abort] missing D90 reference inputs" >&2; exit 4; }

args="$(<"$ref_args")"
args="${args/--seeds 0 /--seeds $seed }"
if [[ $args =~ --stage2_frozen_norm_ckpt\ ([^ ]+) ]]; then
  old="${BASH_REMATCH[1]}"
  new="$d28_root/${old#*/outputs_allpests_e5d_asym5_max140_20260804/}"
  [[ "$new" != "$d28_root/$old" && -f "$new" ]] || { echo "[abort] frozen-norm D28 checkpoint not found: $new" >&2; exit 4; }
  args="${args/"$old"/$new}"
fi
if [[ "${EXPB_DRY_RUN:-0}" == 1 ]]; then printf '%s\n' "$args"; exit 0; fi

cd "$repo"
export ALLPESTS_OUT_ROOT="$out_root/$year/seed$seed"
export OUT_ROOT="$ALLPESTS_OUT_ROOT" WANDB_MODE=disabled WBPH_EXPB_HISTORY_GATE=1
unset WANDB_PROJECT WANDB_ENTITY
source "$e5d/common.sh"
export_e5d_env
mkdir -p "$out" "$proot/clean" "$proot/logs"
for f in split_assignment.json split_manifest.csv split_overlap_checks.json; do
  cp -p "$source_root/clean/$f" "$proot/clean/$f"
done
printf '%s\n' "$args" > "$out/train_args.txt"
printf '%s\n' "[ExpB] eval_year=$year seed=$seed reference=$source_root history_gate=1"
PYTHONPATH="$VENDOR:$CS" "$PY" -u "$VENDOR/_patched_train.py" --eval_year "$year" --assign "$assign" -- $args --out_root "$out" 2>&1 | tee "$out/train.log"
PYTHONPATH="$VENDOR:$CS" "$PY" "$e5d/pest_grid.py" --pest WBPH --mode clean --years "$year" --force 2>&1 | tee "$proot/logs/grid_clean.log"
PYTHONPATH="$VENDOR:$CS" "$PY" "$e5d/pest_eval.py" --pest WBPH --years "$year" --skip dev 2>&1 | tee "$proot/logs/eval.log"
