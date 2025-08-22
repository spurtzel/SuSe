#!/usr/bin/env python3

import datetime

def parse_timestamp(ts):
    """Parses timestamps of the form HH:MM:SS:ffffff into a datetime object."""
    return datetime.datetime.strptime(ts.strip(), "%H:%M:%S:%f")

def measure_elapsed_time(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    # Find the first "simple | 1 |" line and extract the third field (the timestamp)
    simple_ts_str = None
    for line in lines:
        if line.startswith("simple | 1 |"):
            parts = line.split("|")
            # parts[2] is the timestamp
            simple_ts_str = parts[2]
            break

    if not simple_ts_str:
        raise ValueError("No line found starting with 'simple | 1 |'")

    # Check the second to last line for the "complex" line and extract the second field
    if len(lines) < 2:
        raise ValueError("File doesn't have enough lines to contain a second to last line.")

    complex_line = next(line for line in reversed(lines) if "complex |" in line)
    if not complex_line.startswith("complex |"):
        raise ValueError("Second to last line does not start with 'complex |'")

    parts = complex_line.split("|")
    # parts[1] is the timestamp for the complex line
    complex_ts_str = parts[1]

    # Parse timestamps to datetime objects
    simple_ts = parse_timestamp(simple_ts_str)
    complex_ts = parse_timestamp(complex_ts_str)

    # Compute elapsed time in seconds (complex - simple)
    elapsed = complex_ts - simple_ts
    return elapsed.total_seconds()

if __name__ == "__main__":
    filename = "0.log"
    result = measure_elapsed_time(filename)
    print(f"{result} seconds")
