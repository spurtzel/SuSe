#!/usr/bin/env python3

import sys
import datetime

def create_lines(N, filename="trace_0.csv"):
    current_time = datetime.datetime.now()
    letters = ["A", "B", "C", "D"]
    counter = 1
    lines = []

    for letter in letters:
        for _ in range(N):
            timestamp_str = current_time.strftime("%H:%M:%S")
            lines.append(f"{timestamp_str},{letter},{counter}\n")
            current_time += datetime.timedelta(seconds=1)
            counter += 1

    with open(filename, "w") as f:
        f.writelines(lines)
    print(f"Trace file written to {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <N>")
        sys.exit(1)
    
    N = int(sys.argv[1])
    create_lines(N)
