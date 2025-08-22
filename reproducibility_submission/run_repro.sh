#!/usr/bin/env bash
set -euo pipefail

IMAGE="paper-repro:latest"

# Citi Bike dataset
CITIBIKE_URL='https://box.hu-berlin.de/f/b791c68aedcc4b578e29/?dl=1'
CITIBIKE_NAME='202307-citibike-tripdata.csv'
CITIBIKE_DEST0="real_world_experiments/citi_bike/query0/${CITIBIKE_NAME}"
CITIBIKE_DEST1="real_world_experiments/citi_bike/query1/${CITIBIKE_NAME}"

# Flink jar
BEISPIEL_DIR="efficiency/flink_core_rematch/FLINK/flink_cep/java-cep/target"
BEISPIEL_TAR="${BEISPIEL_DIR}/beispiel-1.0-SNAPSHOT.jar.tar.gz"
BEISPIEL_JAR="${BEISPIEL_DIR}/beispiel-1.0-SNAPSHOT.jar"

download_file() {
  local url="$1" out="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 --retry-delay 2 -o "$out" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$out" "$url"
  else
    echo "[run_repro] ERROR: need 'curl' or 'wget' to download dataset." >&2
    return 1
  fi
}

ensure_citibike_dataset() {
  local need_download=0
  for f in "$CITIBIKE_DEST0" "$CITIBIKE_DEST1"; do
    if [[ -s "$f" ]]; then
      echo "[run_repro] found dataset: $f ($(du -h "$f" | cut -f1))"
    else
      need_download=1
    fi
  done

  if [[ "$need_download" -eq 0 ]]; then
    return 0
  fi

  echo "[run_repro] downloading Citi Bike dataset (one-time)..."
  mkdir -p "$(dirname "$CITIBIKE_DEST0")" "$(dirname "$CITIBIKE_DEST1")"

  local tmp
  tmp="$(mktemp)"
  trap 'rm -f "$tmp" >/dev/null 2>&1 || true' EXIT

  download_file "$CITIBIKE_URL" "$tmp"

  if [[ ! -s "$tmp" ]]; then
    echo "[run_repro] ERROR: dataset download produced an empty file." >&2
    exit 1
  fi

  cp -f "$tmp" "$CITIBIKE_DEST0"
  cp -f "$tmp" "$CITIBIKE_DEST1"
  echo "[run_repro] dataset placed at:"
  echo "  - $CITIBIKE_DEST0"
  echo "  - $CITIBIKE_DEST1"
}


ensure_flink_jar_unpacked() {
  if [[ -f "$BEISPIEL_JAR" ]]; then
    echo "[run_repro] found jar: $BEISPIEL_JAR"
  elif [[ -f "$BEISPIEL_TAR" ]]; then
    echo "[run_repro] unpacking: $BEISPIEL_TAR"
    tar -xzf "$BEISPIEL_TAR" -C "$BEISPIEL_DIR"
    echo "[run_repro] unpacked jar: $BEISPIEL_JAR"
  else
    echo "[run_repro] NOTE: archive not found, skipping: $BEISPIEL_TAR"
  fi
}

ensure_flink_jar_unpacked
ensure_citibike_dataset

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build -t "$IMAGE" .
fi

PROGRESS_PERIOD="${PROGRESS_PERIOD:-600}"

WATCHER_PID=""
cleanup() {
  if [[ -n "$WATCHER_PID" ]] && kill -0 "$WATCHER_PID" 2>/dev/null; then
    echo "[run_repro] stopping progress watcher (pid=$WATCHER_PID)"
    kill "$WATCHER_PID" 2>/dev/null || true
    wait "$WATCHER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ -x ./progress_watcher.sh ]]; then
  ./progress_watcher.sh -r . -p "$PROGRESS_PERIOD" &
  WATCHER_PID=$!
  echo "[run_repro] started progress watcher (pid=$WATCHER_PID, period=${PROGRESS_PERIOD}s)"
else
  echo "[run_repro] NOTE: ./progress_watcher.sh not found or not executable; skipping watcher."
fi

docker run --rm -v "$PWD":/work -w /work \
  -e MPLBACKEND=Agg \
  -e PYTHONUNBUFFERED=1 -e PYTHONIOENCODING=UTF-8 \
  "$IMAGE" \
  bash -lc '
    set -e
    echo "[run_repro] ensuring execute permissions (in container)..."
    find . -type f \
      \( -name "*.sh" -o -name "summary_selector" -o -name "rematch" \
         -o \( -path "*/FLINK/flink_cep/deploying/*" ! -name "*.*" \) \
      \) -exec chmod +x {} + 2>/dev/null || true
     echo "[run_repro] execute permissions set."
     python3 -u run_all.py # add --extensive-reproducibilty for same sample size per experiment as in the paper
  '
