#!/usr/bin/env bash
# Run one tmux stage, persist its terminal state, and signal tmux wait-for.
set -euo pipefail
usage() { echo "usage: $0 --stage NAME --state-file PATH --log-file PATH --signal TOKEN -- command [args...]" >&2; exit 64; }
stage=; state=; log=; signal=
while (($#)); do
  case "$1" in
    --stage) stage="$2"; shift 2 ;;
    --state-file) state="$2"; shift 2 ;;
    --log-file) log="$2"; shift 2 ;;
    --signal) signal="$2"; shift 2 ;;
    --) shift; break ;;
    *) usage ;;
  esac
done
[[ -n "$stage" && -n "$state" && -n "$log" && -n "$signal" && $# -gt 0 ]] || usage
mkdir -p "$(dirname "$state")" "$(dirname "$log")"
started=$(date -Is)
printf '{"stage":"%s","status":"RUNNING","started_at":"%s"}\n' "$stage" "$started" >"$state"
set +e
"$@" >"$log" 2>&1
rc=$?
set -e
finished=$(date -Is)
if ((rc == 0)); then status=COMPLETED; else status=FAILED; fi
tmp="$state.tmp.$$"
printf '{"stage":"%s","status":"%s","exit_code":%d,"started_at":"%s","finished_at":"%s","log_file":"%s"}\n' "$stage" "$status" "$rc" "$started" "$finished" "$log" >"$tmp"
mv "$tmp" "$state"
tmux wait-for -S "$signal"
exit "$rc"
