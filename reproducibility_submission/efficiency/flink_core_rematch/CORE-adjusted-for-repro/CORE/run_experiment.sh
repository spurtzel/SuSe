#!/bin/bash

replacement_stream_sizes=("4" "8" "16" "32" "64" "128" "256" "512" "1024" "2048") # "4096")

rm -f times_core.txt

file_path="./susequeries/stream_data.txt"

original_string=$(cat "$file_path")

prefix="${original_string%_*}_4"
suffix="${original_string##*.}"

new_string="${prefix}.${suffix}" # Ensure only one period is used here, right before the suffix
echo "$new_string" > "$file_path"


for replacement in "${replacement_stream_sizes[@]}"; do
    echo "===== Replacement: $replacement ====="
    start=$(date +%s.%N)
    java -Xmx50G -jar CORE-FAT-1.0-SNAPSHOT.jar -f -q ./susequeries/query_data.txt -s ./susequeries/stream_data.txt -o -l
    end=$(date +%s.%N)
    echo "Input length: ${replacement}"
    elapsed=$(awk -v start="$start" -v end="$end" 'BEGIN {printf "%.6f", end - start}')
    {
         echo "Input length: ${replacement}"
         echo "${elapsed} seconds"
    } >> times_core.txt
    if [ $? -eq 0 ]; then
        echo "Java program completed successfully. Modifying the file with replacement: $replacement."

        original_string=$(cat "$file_path")

        prefix="${original_string%_*}_"

        suffix="${original_string##*.}"

        new_string="${prefix}${replacement}.${suffix}"

        echo "$new_string" > "$file_path"

        echo "File has been modified with replacement: $replacement. Start experiment with new stream size."
    else
        echo "Java program failed. Skipping file modification."
    fi
done

echo "Experiments completed."

