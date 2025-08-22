#!/bin/bash
set -eo pipefail

QUERIES=("A(B|G)*A" "A*G(A|B)*G*A")
SUMMARY_SIZES=(100 250 500)
TIME_WINDOW_SIZES=(100 250 500)
STREAM_SIZES=(462028)
TIMES_TO_LIVE=(462028)
PROB_DISTRIBUTIONS=("real_world_data_set")
EVAL_TIMESTAMPS_COUNTS=(400)
EVAL_TIMESTAMPS_PROB_DISTS=("uniform")
NUM_OF_RUNS=(1)
FILE_NAMES=("NASDAQ_20151102_1.txt")

SEEDS=(12233 24969 18355 22349 12701 11641 19403 1250 27936 13434 29891 3638 10151 15807 30417 4082 28888 10342)

rm -f report.csv
rm -f seeds.txt
rm -f *.probs

for query in "${QUERIES[@]}"
do
seed_index=0
        for time_window_size in "${TIME_WINDOW_SIZES[@]}"
        do
                for summary_size in "${SUMMARY_SIZES[@]}"
                do
                        for stream_size in "${STREAM_SIZES[@]}"
                        do
                                for time_to_live in "${TIMES_TO_LIVE[@]}"
                                do
                                        for prob_distribution in "${PROB_DISTRIBUTIONS[@]}"
                                        do
                                                for eval_timestamp_count in "${EVAL_TIMESTAMPS_COUNTS[@]}"
                                                do
                                                        for eval_timestamp_dist in "${EVAL_TIMESTAMPS_PROB_DISTS[@]}"
                                                        do
                                                                for ((run=1; run<=NUM_OF_RUNS; run++))
                                                                do
                                                                        RANDOM_SEED=${SEEDS[$seed_index]}
                                                                        ((seed_index += 1))
                                                                        bash run_test.sh \
                                                                                ${summary_size} \
                                                                                ${time_window_size} \
                                                                                ${stream_size} \
                                                                                ${time_to_live} \
                                                                                ${prob_distribution} \
                                                                                ${eval_timestamp_count} \
                                                                                ${eval_timestamp_dist} \
                                                                                ${RANDOM_SEED} \
                                                                                "${query}"\
                                                                                ${FILE_NAMES[0]} > /dev/null &
                                                                done
                                                        done
                                                done
                                        done
                                done
                        done
                done
        done
done

wait
