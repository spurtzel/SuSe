#!/usr/bin/env bash
set -euo pipefail

rm -f times_flink.txt

for trace in $(ls traces/trace_*.csv | sort -V); do
    rm -f trace_0.csv
    cp "$trace" trace_0.csv
    echo "Input length: $(wc -l < trace_0.csv)" >> times_flink.txt

    ../../run_local "../../example_inputs/SEQ(A,B,C)/" 1 2 &
    pid=$!

    watch=0.log      
    idle=300          
    grace=5          

    if [[ -f $watch ]]; then
        last_change=$(stat -c %Y "$watch" 2>/dev/null || stat -f %m "$watch")
    else
        last_change=$(date +%s)
    fi

    while kill -0 "$pid" 2>/dev/null; do
        sleep 1

        if [[ -f $watch ]]; then
            mtime=$(stat -c %Y "$watch" 2>/dev/null || stat -f %m "$watch")
            (( mtime != last_change )) && last_change=$mtime
        fi

        if (( $(date +%s) - last_change >= idle )); then
            echo " $watch idle for $idle s -> terminating $pid" >&2
            kill -TERM "$pid"
            sleep "$grace"
            kill -KILL "$pid" 2>/dev/null || true
            break
        fi
    done

    wait "$pid" 2>/dev/null || true
    python run_time_determiner.py >> times_flink.txt
done
