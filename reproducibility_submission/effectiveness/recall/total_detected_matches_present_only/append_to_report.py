import argparse
import json
import os

def main():
	parser = argparse.ArgumentParser(description='Merge data in plot format')
	parser.add_argument('--summary_size', default=None, type=int)
	parser.add_argument('--time_window_size', default=None, type=int)
	parser.add_argument('--time_to_live', default=None, type=int)
	parser.add_argument('--stream_size', default=None, type=int)
	parser.add_argument('--query', default=None, type=str)
	parser.add_argument('--distribution_name', default=None, type=str)
	parser.add_argument('--timestamp_distribution_name', default=None, type=str)
	parser.add_argument('--random_seed', default=None, type=int)
	parser.add_argument('--fifo_report', default=None, type=str)
	parser.add_argument('--random_report', default=None, type=str)
	parser.add_argument('--suse_report', default=None, type=str)
	parser.add_argument('--target', default=None, type=str)
	args = parser.parse_args()

	with open(args.fifo_report) as f:
		fifo_report = json.load(f)

	with open(args.random_report) as f:
		random_report = json.load(f)

	with open(args.suse_report) as f:
		suse_report = json.load(f)

	values = dict()
	values["Summary Size"] = args.summary_size
	values["Query"] = args.query
	values["Time Window Size"] = args.time_window_size
	values["stream_size"] = args.stream_size
	values["Alphabet Probability Distribution"] = args.distribution_name
	values["Random Seed"] = args.random_seed
	values["Time to live"] = args.time_to_live
	
	values["Number Evaluation Timestamps"] = len(fifo_report["observed_timestamps"])
	values["Evaluation Timestamps"] = fifo_report["observed_timestamps"]
	values["Evaluation Timestamps Probability Distribution"] = args.timestamp_distribution_name
	
	values["SuSe Complete Matches"] = suse_report["observed_matches"]
	values["Random Complete Matches"] = random_report["observed_matches"]
	values["FIFO Complete Matches"] = fifo_report["observed_matches"]
	
	values["Final SuSe Complete Matches"] = suse_report["final_matches"]
	values["Final Random Complete Matches"] = random_report["final_matches"]
	values["Final FIFO Complete Matches"] = fifo_report["final_matches"]
	
	values["Final SuSe Partial Matches"] = suse_report["final_partial_matches"]
	values["Final Random Partial Matches"] = random_report["final_partial_matches"]
	values["Final FIFO Partial Matches"] = fifo_report["final_partial_matches"]
	
	values["Ratio Random/SuSe"] = [ int(r)/int(s) if int(r) > 0 and int(s) > 0 else 1/int(s) if int(r) == 0 and int(s) > 0 else int(r)/1 if int(r) > 0 and int(s) == 0 else 0 for r,s in zip(random_report["observed_matches"], suse_report["observed_matches"]) ]
	values["Ratio SuSe/Random"] = [ int(s)/int(r) if int(r) > 0 and int(s) > 0 else 1/int(r) if int(s) == 0 and int(r) > 0 else int(s)/1 if int(s) > 0 and int(r) == 0 else 0 for r,s in zip(random_report["observed_matches"], suse_report["observed_matches"]) ]
	
	values["Ratio FIFO/SuSe"] = [ int(f)/int(s) if int(f) > 0 and int(s) > 0 else 1/int(s) if int(f) == 0 and int(s) > 0 else int(f)/1 if int(f) > 0 and int(s) == 0 else 0 for f,s in zip(fifo_report["observed_matches"], suse_report["observed_matches"]) ]
	values["Ratio SuSe/FIFO"] = [ int(s)/int(f) if int(f) > 0 and int(s) > 0 else 1/int(f) if int(s) == 0 and int(f) > 0 else int(s)/1 if int(s) > 0 and int(f) == 0 else 0 for f,s in zip(fifo_report["observed_matches"], suse_report["observed_matches"]) ]
	
	values["Total Ratio Random/SuSe"] = int(random_report["final_matches"])/int(suse_report["final_matches"]) if int(random_report["final_matches"]) > 0 and int(suse_report["final_matches"]) > 0 else 1/int(suse_report["final_matches"]) if int(random_report["final_matches"]) == 0 and int(suse_report["final_matches"]) > 0 else int(random_report["final_matches"])/1 if int(random_report["final_matches"]) > 0 and int(suse_report["final_matches"]) == 0 else 0
	values["Total Ratio SuSe/Random"] = int(suse_report["final_matches"])/int(random_report["final_matches"]) if int(random_report["final_matches"]) > 0 and int(suse_report["final_matches"]) > 0 else 1/int(random_report["final_matches"]) if int(suse_report["final_matches"]) == 0 and int(random_report["final_matches"]) > 0 else int(suse_report["final_matches"])/1 if int(suse_report["final_matches"]) > 0 and int(random_report["final_matches"]) == 0 else 0
	
	values["Total Ratio FIFO/SuSe"] = int(fifo_report["final_matches"])/int(suse_report["final_matches"]) if int(fifo_report["final_matches"]) > 0 and int(suse_report["final_matches"]) > 0 else 1/int(suse_report["final_matches"]) if int(fifo_report["final_matches"]) == 0 and int(suse_report["final_matches"]) > 0 else int(fifo_report["final_matches"])/1 if int(fifo_report["final_matches"]) > 0 and int(suse_report["final_matches"]) == 0 else 0
	values["Total Ratio SuSe/FIFO"] = int(suse_report["final_matches"])/int(fifo_report["final_matches"]) if int(fifo_report["final_matches"]) > 0 and int(suse_report["final_matches"]) > 0 else 1/int(fifo_report["final_matches"]) if int(suse_report["final_matches"]) == 0 and int(fifo_report["final_matches"]) > 0 else int(suse_report["final_matches"])/1 if int(suse_report["final_matches"]) > 0 and int(fifo_report["final_matches"]) == 0 else 0
	
	values["SuSe Total Detected Partial Matches"] = suse_report["detected_partial_matches"]
	values["Random Total Detected Partial Matches"] = random_report["detected_partial_matches"]
	values["FIFO Total Detected Partial Matches"] = fifo_report["detected_partial_matches"]
	
	values["SuSe Total Detected Matches"] = suse_report["detected_matches"]
	values["Random Total Detected Matches"] = random_report["detected_matches"]
	values["FIFO Total Detected Matches"] = fifo_report["detected_matches"]

	values["Execution Time SuSe"] = fifo_report["runtime_ns"]
	values["Execution Time Random"] = random_report["runtime_ns"]
	values["Execution Time FIFO"] = random_report["runtime_ns"]
	
	values["Initialization Time SuSe"] = fifo_report["initialization_time_ns"]
	values["Initialization Time Random"] = random_report["initialization_time_ns"]
	values["Initialization Time FIFO"] = random_report["initialization_time_ns"]
	
	values["Average Latency SuSe"] = fifo_report["average_latency_ns"]
	values["Average Latency Random"] = random_report["average_latency_ns"]
	values["Average Latency FIFO"] = random_report["average_latency_ns"]
	
	values["Max Latency SuSe"] = fifo_report["max_latency_ns"]
	values["Max Latency Random"] = random_report["max_latency_ns"]
	values["Max Latency FIFO"] = random_report["max_latency_ns"]
	
	values["Min Latency SuSe"] = fifo_report["min_latency_ns"]
	values["Min Latency Random"] = random_report["min_latency_ns"]
	values["Min Latency FIFO"] = random_report["min_latency_ns"]

	if not os.path.exists(args.target) or os.path.getsize(args.target)<=0:
		with open(args.target,'w',newline='') as csv:
			print(*sorted(values.keys()),sep=',',file = csv)

	with open(args.target,'a',newline='') as csv:
		print(*[f"\"{values[key]}\"" for key in sorted(values.keys())],sep=',',file = csv)
	
if __name__ == "__main__":
	main()

