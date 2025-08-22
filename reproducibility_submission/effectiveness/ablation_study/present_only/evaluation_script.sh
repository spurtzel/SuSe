#!/bin/bash
set -eo pipefail

QUERIES=("a(b*c)*d(e|f)g*")
SUMMARY_SIZES=(100 250 500 1000)
TIME_WINDOW_SIZES=(50 100 250)
STREAM_SIZES=(100000)
TIMES_TO_LIVE=(100000)
PROB_DISTRIBUTIONS=("zipf")
EVAL_TIMESTAMPS_COUNTS=(50)
EVAL_TIMESTAMPS_PROB_DISTS=("poisson")
NUM_OF_RUNS=(5)

SEEDS=(29123 30955 19587 27456 19225 3362 3582 23878 24601 15726 19800 12039 30710 8577 29250 18184 19361 329 23627 4291 11413 11550 24818 14300 9426 24406 25428 14452 13508 1077 22530 2159 9051 8081 5367 19047 13841 13256 22885 20057 29294 30394 3312 12178 5039 6581 24708 25669 13999 22752 16062 15186 23732 10794 11103 22362 15209 22879 3070 20339 3560 21166 26457 20225 26591 26121 7713 1751 5001 17124 24117 8123 18396 3877 7722 26566 6331 9898 32687 27773 6960 735 17106 8085 14863 29259 29531 18398 7257 1887 1767 16775 4303 31348 30028 6198 17657 2174 9508 15404 29188 16342 31849 27051 31080 32639 3593 22951 16574 28587 28171 14128 9542 5888 25302 11854 2575 28418 8818 10558 14079 13758 22119 2754 3937 22377 18254 2117 12809 8113 24129 6831 9396 29637 16736 4910 29701 9877 12911 4831 10872 21839 21179 6632 21389 23065 10861 19605 4071 26605 23769 28143 14769 13855 12492 948 22915 14756 16631 24837 22071 7532 11260 28242 23538 27066 24906 12393 25943 16451 5281 13615 20704 20439 22353 2553 25872 15028 9540 29713 27868 19197 1918 30287 11485 2424 2975 32577 12454 31019 25772 1499 5068 25111 675 24461 7943 3548 3319 28547 21074 30509 28153 30468 8573 13984 2936 19576 12767 27725 961 3407 24712 2257 31095 1880 3905 20248 18426 8047 24321 31334 32260 27778 5088 15825 244 26845 14525 14605 32253 29197 26700 19806 19932 14223 30170 4458 19419 3166 7532 6822 9501 8390 6518 512 28992 4805 13853 28308 24596 22177 18162 21815 13087 22282 23041 11831 21629 29111 29497 30007 12275 21138 24675 24625 5280 4490 27356 24058 22882 8423 21004 224 4980 6492 15987 24821 14939 28561 4193 18547 5566 10057 29995 19669 27758 30252 15729 6037 28223 20079 23723 24941 21485 3670 13018 31873 7022 6837)

rm -f report.csv
rm -f seeds.txt

seed_index=0

for query in "${QUERIES[@]}"
do
        for summary_size in "${SUMMARY_SIZES[@]}"
        do
                for time_window_size in "${TIME_WINDOW_SIZES[@]}"
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
									if (( seed_index >= ${#SEEDS[@]} )); then
                                                                        	seed_index=0
									fi
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
                wait
        done
done
