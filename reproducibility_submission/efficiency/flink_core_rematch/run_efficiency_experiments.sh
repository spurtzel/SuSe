#!/usr/bin/env bash

set -u -o pipefail

INVOCATION_DIR="$(pwd -P)"

run_and_collect() {
  local script_path="$1"   
  local artifact="$2"      

  local script_dir base artifact_src rc cprc
  script_dir="$(cd "$(dirname "$script_path")" && pwd -P)"
  base="$(basename "$script_path")"

  echo "==> Running $base in $script_dir"
  (
    set +e  
    cd "$script_dir" || exit 1

    bash "./$base"
    rc=$?

    # resolve artifact path
    if [[ "$artifact" = /* ]]; then
      artifact_src="$artifact"
    else
      artifact_src="$script_dir/$artifact"
    fi

    if [[ -f "$artifact_src" ]]; then
      echo "   • copying $(basename "$artifact_src") -> $INVOCATION_DIR/"
      cp -v -- "$artifact_src" "$INVOCATION_DIR/"
      cprc=$?
    else
      echo "   • artifact not found: $artifact_src" >&2
      cprc=1
    fi

    if (( rc != 0 )); then
      echo "   • WARNING: $base exited with code $rc" >&2
    fi
    if (( cprc != 0 )); then
      echo "   • WARNING: copy failed for $artifact_src" >&2
    fi

    # Always succeed so the rest of the pipeline runs
    exit 0
  )
}

run_and_collect "FLINK/flink_cep/deploying/example_inputs/SEQ(A,B,C)/run_flink_experiment.sh" \
                "times_flink.txt"

run_and_collect "CORE-adjusted-for-repro/CORE/run_experiment.sh" \
                "times_core.txt"

run_and_collect "REmatch-no-output/evaluation_script.sh" \
                "times_rematch.txt"

run_and_collect "suse/evaluation_script_suse.sh" \
                "report.csv"

echo "RegEx CEP engines experiments finished. Artifacts copied to: $INVOCATION_DIR"
