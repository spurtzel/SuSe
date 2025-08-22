#!/bin/bash
set -eo pipefail

QUERIES=("a(b*c)*d(e|f)g*")
SUMMARY_SIZES=(10 20 50 100 250 500 1000 2500 5000) 
TIME_WINDOW_SIZES=(10 25 50 100 250 500) 
STREAM_SIZES=(100000)
TIMES_TO_LIVE=(100000)
PROB_DISTRIBUTIONS=("uniform")
EVAL_TIMESTAMPS_COUNTS=(1)
EVAL_TIMESTAMPS_PROB_DISTS=("uniform")
NUM_OF_RUNS=(3)

rm -f report.csv
rm -f seeds.txt

for query in "${QUERIES[@]}"
do
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
									RANDOM_SEED=${RANDOM}
									bash run_test.sh \
										${summary_size} \
										${time_window_size} \
										${stream_size} \
										${time_to_live} \
										${prob_distribution} \
										${eval_timestamp_count} \
										${eval_timestamp_dist} \
										${RANDOM} \
										"${query}" >/dev/null &
								done
							done
						done
					done
				done
			done
                        wait
		done
	done
done
