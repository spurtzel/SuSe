#!/bin/bash
set -eo pipefail

QUERIES=("FDCCCC" "(FDCCCC)|(EFCBDED)" "(FDCCCC)|(EFCBDED)|(EAD)" "(FDCCCC)|(EFCBDED)|(EAD)|(DDE)" "(FDCCCC)|(EFCBDED)|(EAD)|(DDE)|(EEDEABFF)" "(FDCCCC)|(EFCBDED)|(EAD)|(DDE)|(EEDEABFF)|(CAADAFC)" "(FDCCCC)|(EFCBDED)|(EAD)|(DDE)|(EEDEABFF)|(CAADAFC)|(EDEB)" "(FDCCCC)|(EFCBDED)|(EAD)|(DDE)|(EEDEABFF)|(CAADAFC)|(EDEB)|(BBFDDF)")
SUMMARY_SIZES=(500) 
TIME_WINDOW_SIZES=(100) 
STREAM_SIZES=(10000)
TIMES_TO_LIVE=(10000)
PROB_DISTRIBUTIONS=("uniform")
EVAL_TIMESTAMPS_COUNTS=(25)
EVAL_TIMESTAMPS_PROB_DISTS=("poisson")
NUM_OF_RUNS=(5)


SEEDS=(18328 29418 12162 29069 18185 26596 17495 25388 13933 26034 8556 15321 576 28724 24397 11901 6313 8590 12675 8361 9755 28662 28325 9393 8295 4496 19344 20900 29435 26856 12660 9993 23111 8411 10597 10669 8177 24212 20595 8044 18695 11528 18627 10636 26129 6173 4363 4873 4965 25554 25530 5031 13973 10514 327 8158 7358 10555 13044 31681 32762 8767 17185 615 13692 21198 12393 8070 3528 25497 14624 20257 9165 11618 29128 31721 20740 21732 23587 1873 17888 11913 21568 15106 29677 19456 29031 20872 13710 21367 20086 22118 9417 18448 931 1765 17996 2630 14961 11754 27714 32719 21138 12591 31674 112 21442 22334 17421 10799 26561 27098 7990 26551 11300 22631 11668 29582 8606 2210 24724 29261 738 7112 31918 8075 793 21998 22528 19402 4518 23928 16849 24479 23161 9741 7872 16944 30217 26122 26322 24547 32086 2900 4797 13997 4654 11342 5393 14856 19645 26764 2287 14341 1330 3954 1825 16199 105 2394 14305 23699 13221 31750 17405 11172 3995 22272 27891 2922 15844 12522 29635 8515 26418 7784 6093 11948 28354 31414 20309 9792 7062 25296 27113 31247 8093 2922 21068 22593 8435 20670 6841 20786 10811 32334 23367 15823 14919 16710)


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
                                                                        ((seed_index+=1))
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
