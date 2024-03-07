# SuSe: Summary Selection for Regular Expression Subsequence Aggregation over Streams

## Requirements

### Build Tools
- Make
- CMake (version >= 3.12.0)
- C++ compiler supporting C++20 or higher


### Python Script Requirements
- Python3 (version >= 3.10.9)
- Required Python Libraries:
    - argparse
    - json
    - matplotlib
    - numpy
    - re
    - scipy
    - os

  
### Linux/Unix programs
- The execution scripts utilize the following Linux/Unix programs:
    - echo, wait, head, trap, cat, flock

  

## Compilation Steps
1. Clone the repository.
2.  `cd` into the project directory.
3. Create a build directory: `mkdir build`
4. Change to the build directory: `cd build`
5. Generate build files: `cmake ..`
6. Compile and link the project: `make`

  

## Execution Steps (Linux/Unix)
1.  `cd` into the `build` directory.
2. Execute the `evaluation_script.sh` script: `bash evaluation_script.sh`

  

## Parameters
- When running the program, you can change the following start parameters in the `execution_script.sh` file.

### QUERIES
-  `QUERIES=("ABC" "A(B*C)*D")`: Specifies the Regular Expression (RegEx) queries.

  
### SUMMARY_SIZES
-  `SUMMARY_SIZES=(10 100 1000)`: Specifies the summary sizes.


### TIME_WINDOW_SIZES
-  `TIME_WINDOW_SIZES=(100 250 500)`: Specifies the time window sizes.


### STREAM_SIZES
-  `STREAM_SIZES=(10000 100000)`: Specifies the stream sizes to process.


### TIMES_TO_LIVE
-  `TIMES_TO_LIVE=(100000)`: Specifies the time-to-live (TTL) of an element.


### PROB_DISTRIBUTIONS
-  `PROB_DISTRIBUTIONS=("zipf" "uniform" "normal")`: Specifies the alphabet probability distribution.


### EVAL_TIMESTAMPS_COUNTS
-  `EVAL_TIMESTAMPS_COUNTS=(20)`: Specifies the number of evaluation timestamps.


### EVAL_TIMESTAMPS_PROB_DISTS
-  `EVAL_TIMESTAMPS_PROB_DISTS=("poisson" "uniform")`: Specifies the evaluation timestamp probability distribution.

  
## Supported RegEx Operators
### Concatenation
- The adjacency of two characters or expressions signifies their concatenation.

### Union `|`
- The `|` symbol is used to denote the union of two expressions.

### Kleene Star `*`
- The `*` symbol indicates zero or more occurrences of the preceding expression.


### -- Syntactic Sugar --
### Kleene Plus `+`
- The `+` symbol signifies one or more occurrences of the preceding expression.


### Optional `?`
- The `?` symbol stands for zero or one occurrence of the preceding expression.


### Wildcard `.`
- The `.` symbol matches any character from the alphabet.

## Attributes Table
### The `evaluation_script.sh` creates a .csv file `report.csv` which includes information about the following results: 

| Attribute                                      | Description                                       |
|------------------------------------------------|---------------------------------------------------|
| Alphabet Probability Distribution              | ...                                               |
| Average Latency FIFO                           | ...                                               |
| Average Latency Random                         | ...                                               |
| Average Latency SuSe                           | ...                                               |
| Evaluation Timestamps                          | ...                                               |
| Evaluation Timestamps Probability Distribution | ...                                               |
| Execution Time FIFO                            | ...                                               |
| Execution Time Random                          | ...                                               |
| Execution Time SuSe                            | ...                                               |
| FIFO Complete Matches                          | ...                                               |
| FIFO Total Detected Matches                    | The number of *all* detected matches by FIFO baseline.|
| FIFO Total Detected Partial Matches            | ...                                               |
| Final FIFO Complete Matches                    | ...                                               |
| Final FIFO Partial Matches                     | ...                                               |
| Final Random Complete Matches                  | ...                                               |
| Final Random Partial Matches                   | ...                                               |
| Final SuSe Complete Matches                    | Number of matches in the final summary.           |
| Final SuSe Partial Matches                     | ...                                               |
| Initialization Time FIFO                       | ...                                               |
| Initialization Time Random                     | ...                                               |
| Initialization Time SuSe                       | Required pre-processing time.                     |
| Max Latency FIFO                               | ...                                               |
| Max Latency Random                             | ...                                               |
| Max Latency SuSe                               | ...                                               |
| Min Latency FIFO                               | ...                                               |
| Min Latency Random                             | ...                                               |
| Min Latency SuSe                               | ...                                               |
| Number Evaluation Timestamps                   | ...                                               |
| Query                                          | ...                                               |
| Random Complete Matches                        | ...                                               |
| Random Seed                                    | ...                                               |
| Random Total Detected Matches                  | The number of *all* detected matches by random baseline.|
| Random Total Detected Partial Matches          | ...                                               |
| Ratio FIFO/SuSe                                | ...                                               |
| Ratio Random/SuSe                              | ...                                               |
| Ratio SuSe/FIFO                                | ...                                               |
| Ratio SuSe/Random                              | ...                                               |
| SuSe Complete Matches                          | ...                                               |
| SuSe Total Detected Matches                    | The number of *all* detected matches by SuSe.     |
| SuSe Total Detected Partial Matches            | ...                                               |
| Summary Size                                   | ...                                               |
| Time Window Size                               | ...                                               |
| Time to live                                   | ...                                               |
| Total Ratio FIFO/SuSe                          | ...                                               |
| Total Ratio Random/SuSe                        | ...                                               |
| Total Ratio SuSe/FIFO                          | The final total match ratio.                      |
| Total Ratio SuSe/Random                        | The final total match ratio.                      |
| stream_size                                    | ...                                               |

