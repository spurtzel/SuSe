#!/usr/bin/env bash

set -u

ROOT="."
PERIOD=600   # seconds; default = 10 minutes

usage() {
  cat <<EOF
Usage: $(basename "$0") [-r ROOT] [-p PERIOD_SECONDS]

  -r, --root     Root directory to scan (default: .)
  -p, --period   Seconds between reports (default: 600 = 10 minutes)
  -h, --help     Show this help
EOF
}

while (( $# )); do
  case "$1" in
    -r|--root)   ROOT="${2:?}"; shift 2 ;;
    -p|--period) PERIOD="${2:?}"; shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

ROOT="$(cd "$ROOT" && pwd -P)" || { echo "Cannot cd to $ROOT" >&2; exit 1; }

tslog() { printf '[%(%F %T)T] %s\n' -1 "$*"; }

compute_total_for_dir() {
  local dir="$1"
  local runner=""
  for cand in evaluation_script.sh evaluation_script_suse.sh run_efficiency_experiments.sh; do
    if [[ -f "$dir/$cand" ]]; then runner="$dir/$cand"; break; fi
  done
  [[ -n "$runner" ]] || { echo ""; return 0; }

  local assigns
  assigns="$(
    sed -n -E '
      /^\s*(QUERIES|SUMMARY_SIZES|TIME_WINDOW_SIZES|STREAM_SIZES|TIMES_TO_LIVE|PROB_DISTRIBUTIONS|EVAL_TIMESTAMPS_COUNTS|EVAL_TIMESTAMPS_PROB_DISTS|NUM_OF_RUNS)\s*=/{
        s/#.*$//; p;
      }' "$runner"
  )"

  [[ -n "$assigns" ]] || { echo ""; return 0; }

  local counts
  counts="$(
    bash -c '
      set -euo pipefail
      QUERIES=(); SUMMARY_SIZES=(); TIME_WINDOW_SIZES=(); STREAM_SIZES=(); TIMES_TO_LIVE=();
      PROB_DISTRIBUTIONS=(); EVAL_TIMESTAMPS_COUNTS=(); EVAL_TIMESTAMPS_PROB_DISTS=();
      NUM_OF_RUNS=1

      while IFS= read -r line; do
        eval "$line"
      done

      fix() { local n="$1"; if (( n > 0 )); then echo "$n"; else echo 1; fi; }

      num_runs=1
      if declare -p NUM_OF_RUNS >/dev/null 2>&1; then
        if [[ "$(declare -p NUM_OF_RUNS 2>/dev/null)" == declare\ -a* ]]; then
          num_runs="${NUM_OF_RUNS[0]}"
        else
          num_runs="${NUM_OF_RUNS}"
        fi
      fi

      echo "$(fix ${#QUERIES[@]}) \
            $(fix ${#SUMMARY_SIZES[@]}) \
            $(fix ${#TIME_WINDOW_SIZES[@]}) \
            $(fix ${#STREAM_SIZES[@]}) \
            $(fix ${#TIMES_TO_LIVE[@]}) \
            $(fix ${#PROB_DISTRIBUTIONS[@]}) \
            $(fix ${#EVAL_TIMESTAMPS_COUNTS[@]}) \
            $(fix ${#EVAL_TIMESTAMPS_PROB_DISTS[@]}) \
            ${num_runs}"
    ' <<<"$assigns"
  )"

  local q s tw str ttl pd ec ed nr
  read -r q s tw str ttl pd ec ed nr <<<"$counts"
  local total=$(( q * s * tw * str * ttl * pd * ec * ed * nr ))
  echo "$total"
}

last_report=""
last_total=""
last_exp=""

while :; do
  mapfile -t found < <(
    find "$ROOT" -type f -name 'report*.csv' \
      -not -path "$ROOT/runs/*" -not -path "$ROOT/paper/*" \
      -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1
  )

  if (( ${#found[@]} == 0 )); then
    tslog "no report*.csv found under $ROOT; will check again"
    sleep "$PERIOD" || break
    continue
  fi

  line="${found[0]}"
  latest_path="${line#* }"
  [[ -n "$latest_path" ]] || { sleep "$PERIOD" || break; continue; }

  exp_dir="$(dirname "$latest_path")"
  exp_rel="${exp_dir#$ROOT/}"

  if [[ "$latest_path" != "$last_report" ]]; then
    tslog "monitoring: ${exp_rel}/$(basename "$latest_path")"
    last_report="$latest_path"
    last_exp="$exp_rel"
    last_total="$(compute_total_for_dir "$exp_dir")"
    if [[ -n "$last_total" ]]; then
      tslog "[${exp_rel}] total runs = $last_total"
    else
      tslog "[${exp_rel}] total runs unknown (could not parse runner script)"
    fi
  fi

  lines=$(wc -l < "$latest_path" 2>/dev/null || echo 0)
  (( done = lines > 0 ? lines - 1 : 0 ))

  if [[ -n "${last_total}" && "${last_total}" -gt 0 ]]; then
    pct=$(awk -v d="$done" -v t="${last_total}" 'BEGIN{ if (t>0) printf "%.1f", 100.0*d/t; else print "0.0"; }')
    tslog "[${exp_rel}] ${done} of ${last_total} runs finished ~ ${pct}% done"
  else
    tslog "[${exp_rel}] ${done} runs finished (total unknown)"
  fi

  sleep "$PERIOD" || break
done
