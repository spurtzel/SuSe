#!/bin/bash
set -eo pipefail

QUERIES=("abcdefghij" "abcdefghij|gf" "abcdefghij|gfcd" "abcdefghij|gfcdia" "abcdefghij|gfcdiahj")
SUMMARY_SIZES=(500) 
TIME_WINDOW_SIZES=(100) 
STREAM_SIZES=(25000)
TIMES_TO_LIVE=(25000)
PROB_DISTRIBUTIONS=("uniform")
EVAL_TIMESTAMPS_COUNTS=(50)
EVAL_TIMESTAMPS_PROB_DISTS=("poisson")
NUM_OF_RUNS=(10)


SEEDS=(2333 28909 15186 10555 16842 3770 10562 16716 26240 27397 26734 15360 14492 18929 10860 12802 9813 3145 4736 20701 3604 7256 17190 2555 11103 16708 14005 20246 32134 17137 1900 29678 3279 28870 2683 13118 5813 12050 31700 16700 19893 19182 28105 29824 9941 23650 27366 14382 18615 19816 17190 10555 1900 2333 2555 32134 20701 20246 7256 16700 13118 27397 14492 15186 10860 28909 3145 14382 26734 29678 9941 16708 27366 3279 15360 28105 16842 26240 29824 10562 12802 19893 28870 18615 11103 3770 14005 16716 18929 9813 19816 3604 12050 2683 4736 31700 19182 17137 23650 5813 2333 20701 19893 13118 4736 3279 10860 28909 9813 17190 19182 20246 15360 3770 31700 15186 26240 14492 18929 27397 2555 3604 16700 7256 10555 14382 10562 14005 18615 3145 17137 9941 16716 28870 1900 5813 32134 29678 16842 12802 11103 16708 29824 26734 19816 27366 12050 28105 2683 23650 10562 28909 14492 16716 13118 28105 18929 26734 9813 2555 29824 27366 3145 5813 20701 16700 26240 10555 20246 14382 2333 2683 32134 3279 23650 12802 19816 3770 17190 10860 18615 15360 3604 12050 16842 15186 17137 19893 7256 9941 16708 31700 28870 4736 19182 11103 29678 14005 27397 1900 10562 29678 23650 3604 15360 2333 3770 31700 28909 14005 13118 12050 28105 7256 5813 9813 16708 2683 16842 2555 12802 29824 1900 4736 17137 3145 27397 20701 3279 18929 16716 18615 14382 16700 19893 20246 26240 28870 26734 14492 32134 17190 9941 27366 15186 11103 19816 10555 19182 10860)

rm -f report.csv
rm -f seeds.txt

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
                                                                                "${query}" >/dev/null &
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
