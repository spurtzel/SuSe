#!/bin/bash
set -eo pipefail

QUERIES=("a(b*c)*d(e|f)g*")
SUMMARY_SIZES=(500) 
TIME_WINDOW_SIZES=(100) 
STREAM_SIZES=(25000)
TIMES_TO_LIVE=(25000)
PROB_DISTRIBUTIONS=("uniform")
EVAL_TIMESTAMPS_COUNTS=(10 25 50 100 200)
EVAL_TIMESTAMPS_PROB_DISTS=("poisson")
NUM_OF_RUNS=(10)


SEEDS=(177 19565 23005 1976 22501 6362 6909 10532 32363 17330 31228 8222 25387 8881 30154 29438 9832 30693 8258 29461 10389 26434 29136 2704 21809 2475 19424 1443 2304 24487 9560 21512 9116 27117 9320 12534 15371 21638 21509 14578 24917 24507 25974 30699 8796 28912 10341 22498 25926 30968 23470 739 20964 31321 29208 22871 27814 8161 17859 16357 17887 16362 29572 27705 16124 25889 30377 3714 25767 14738 12530 26516 7380 30590 13541 14128 24535 11585 4942 22952 11455 19826 17530 7768 27710 19672 16816 29527 26589 12997 7229 16258 6257 22399 23435 4368 21204 27352 8667 29184 22231 14507 30600 27824 12428 263 26192 21240 8642 12195 7024 11947 20566 4081 402 16536 21941 31295 6080 16792 29446 15367 31248 6865 11976 31532 452 6041 21138 15409 28842 8474 8722 31684 21476 21392 22576 1276 12108 10209 27671 29839 28094 29740 10432 14511 10386 29863 14482 32595 29113 25302 15752 28857 19769 3007 24818 10357 6880 11038 30559 25324 11526 24266 21061 12973 7950 29846 2507 18206 14778 31576 17450 5372 31045 12807 4353 26952 17741 19531 18317 25332 5328 13520 23079 9412 17975 4938 5732 25958 1482 16330 10216 31818 26150 16500 16639 12173 6825 14834 2074 19067 26527 15811 5897 14009 23680 16332 527 20194 26238 20475 8209 20520 19656 19265 21573 22447 20142 7012 18871 235 8205 21085 9606 19565 31869 2283 4004 18481 30710 23526 28424 1845 11047 26954 14502 32680 27711 18382 3407 7772 17991 20602 22182 4799 13096 874 29406 26439)

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
