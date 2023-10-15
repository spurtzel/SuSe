#!/bin/bash

QUERIES=('abcdef*')
SUMMARY_SIZES=(100) 
TIME_WINDOW_SIZES=(50) 
STREAM_SIZES=(200 400)
TIMES_TO_LIVE=(4000)
PROB_DISTRIBUTIONS=("zipf" "normal")
EVAL_TIMESTAMPS_COUNTS=(20)
EVAL_TIMESTAMPS_PROB_DISTS=("uniform")

rm report.csv

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
								bash run_test.sh \
									${summary_size} \
									${time_window_size} \
									${stream_size} \
									${time_to_live} \
									${prob_distribution} \
									${eval_timestamp_count} \
									${eval_timestamp_dist} \
									${RANDOM} \
									"${query}"
							done
						done
					done
				done
			done
		done
	done
done

wait

rm *.probs
