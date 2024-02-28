#!/bin/bash

SUMMARY_SIZE=$1
TIME_WINDOW_SIZE=$2
STREAM_SIZE=$3
TIME_TO_LIVE=$4
PROB_DISTRIBUTION=$5
EVAL_TIMESTAMPS_COUNT=$6
EVAL_TIMESTAMPS_PROB_DIST=$7
RANDOM_SEED=$8
QUERY=$9
INPUT=${10}

echo "Running test with: "
echo "summary_size=${SUMMARY_SIZE}"
echo "time_window_size=${TIME_WINDOW_SIZE}"
echo "stream_size=${STREAM_SIZE}"
echo "time_to_live=${TIME_TO_LIVE}"
echo "prob_distribution=${PROB_DISTRIBUTION}"
echo "eval_timestamp_count=${EVAL_TIMESTAMPS_COUNT}"
echo "eval_timestamp_prob_dist=${EVAL_TIMESTAMPS_PROB_DIST}"
echo "random_seed=${RANDOM_SEED}"
echo "query=${QUERY}"
echo "input=${INPUT}"

EVAL_TIMESTAMPS=$(python3 evaluation_timestamp_generator.py \
	--summary_size=${SUMMARY_SIZE} \
	--stream_size=${STREAM_SIZE} \
	--number_of_evaluation_timestamps=${EVAL_TIMESTAMPS_COUNT} \
	--distribution_name=${EVAL_TIMESTAMPS_PROB_DIST} \
	--random_seed=${RANDOM_SEED}
)

echo "Selected Timestamps: [${EVAL_TIMESTAMPS}]"

QUERY_CHARS=$(echo ${QUERY//[^[:alpha:]]} | grep -o . | sort | uniq | tr -d "\n")
echo "Symbols in query: ${QUERY_CHARS}"

PROB_FILENAME="${QUERY_CHARS}_${PROB_DISTRIBUTION}.probs"
echo "Storing probabilities in: ${PROB_FILENAME}"

declare -A report_files
for strategy in "suse" "fifo" "random"
do
        temp_report_file=$(mktemp)
        echo "Created temporary report file ${temp_report_file}"
        report_files[${strategy}]=${temp_report_file}
        trap "rm -f ${temp_report_file}" 0 2 3 15
		echo -n "${INPUT}" | sed -e "s/./&\n/g" | nl | awk '{print $2 " " $1}' | ./summary_selector \
                --query="${QUERY}" \
                --strategy=${strategy} \
                --probabilities-file=${PROB_FILENAME} \
                --summary-size=${SUMMARY_SIZE} \
                --time-window-size=${TIME_WINDOW_SIZE} \
                --time-to-live=${TIME_TO_LIVE} \
                --evaluation-timestamps=${EVAL_TIMESTAMPS} \
                --report="${temp_report_file}"

        cat ${temp_report_file}
done

echo "All done, merging into report..."
flock --verbose report.csv python3 append_to_report.py \
	--summary_size=${SUMMARY_SIZE} \
	--time_window_size=${TIME_WINDOW_SIZE} \
	--stream_size=${STREAM_SIZE} \
	--time_to_live=${TIME_TO_LIVE} \
	--query="${QUERY}" \
	--distribution_name="${PROB_DISTRIBUTION}" \
	--timestamp_distribution_name="${EVAL_TIMESTAMPS_PROB_DIST}" \
	--random_seed=${RANDOM_SEED} \
	--fifo_report="${report_files[fifo]}" \
	--random_report="${report_files[random]}" \
	--suse_report="${report_files[suse]}" \
	--target="report.csv"

echo "Done, deleting temporary files"

for strategy in "suse" "fifo" "random"
do
	echo ${report_files[${strategy}]}
	rm ${report_files[${strategy}]}
done

echo "..done. Bye :)"
