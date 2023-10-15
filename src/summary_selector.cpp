#include "eviction_strategies.hpp"
#include "nfa.hpp"
#include "regex.hpp"
#include "summary_selector.hpp"

#include <boost/multiprecision/cpp_int.hpp>
#include <boost/multiprecision/cpp_bin_float.hpp>

#include <cxxopts.hpp>

#include <fmt/color.h>
#include <fmt/format.h>
#include <fmt/ostream.h>
#include <fmt/chrono.h>

#include <array>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <optional>
#include <ranges>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using nanoseconds = std::chrono::nanoseconds;
using counter_type = boost::multiprecision::uint128_t;

template <> struct fmt::formatter<counter_type>: fmt::ostream_formatter {}; // enables fmt::print to print values of boost::multiprecision::uint128_t

namespace
{
	std::optional<suse::nfa> try_compile(std::string_view line)
	{
		try
		{
			return suse::parse_regex(line);
		}
		catch(const suse::regex_parse_error& error)
		{
			const auto prefix = line.substr(0,error.location);
			const auto error_char = error.location<line.size()?line.substr(error.location,1):std::string_view{};
			const auto suffix = error.location+1<line.size()?line.substr(error.location+1):std::string_view{};
			fmt::print(fmt::fg(fmt::color::red),"\nAt position {}:\n\n",error.location);
			fmt::print("{}{}{}\n{: >{}}\n",prefix,fmt::styled(error_char,fmt::fg(fmt::color::red)),suffix,"^",error.location+1);
			fmt::print(fmt::fg(fmt::color::red),"Parse error: ");
			fmt::print("{}\n",error.what());

			return std::nullopt;
		}
	}

	std::unordered_map<char,boost::multiprecision::cpp_bin_float_50> load_probabilities(const std::filesystem::path& path)
	{
		std::ifstream in{path};
		std::unordered_map<char,boost::multiprecision::cpp_bin_float_50> probabilities;
		
		char symbol;
		boost::multiprecision::cpp_bin_float_50 probability;
		while(in>>symbol>>probability)
			probabilities[symbol] = probability;

		probabilities[suse::nfa::wildcard_symbol] = 1;
		return probabilities;
	}

	std::unordered_map<char,boost::multiprecision::cpp_bin_float_50> generate_uniform_probabilities(const suse::nfa& nfa)
	{
		std::unordered_map<char,boost::multiprecision::cpp_bin_float_50> probabilities;
		for(const auto& state: nfa.states())
			for(const auto& [symbol,_]: state.transitions)
				if(symbol!=suse::nfa::wildcard_symbol)
					probabilities[symbol] = {};

		const auto uniform_fraction = boost::multiprecision::cpp_bin_float_50{1} / probabilities.size();
		for(auto& [_,prob]: probabilities)
			prob = uniform_fraction;

		probabilities[suse::nfa::wildcard_symbol] = 1;
		return probabilities;
	}

	struct summary_observation
	{
		counter_type matches;
		std::size_t timestamp;
	};
	
	struct run_result
	{
		nanoseconds average_latency{0}, max_latency{0}, min_latency = std::chrono::hours{42};
		std::vector<summary_observation> observations;
		counter_type final_matches, final_partial_matches;
		counter_type detected_matches, detected_partial_matches;
		std::size_t processed_events;
	};
	
	template <typename strategy_type>
	auto run(suse::summary_selector<counter_type>& selector, strategy_type& strategy, const std::unordered_set<std::size_t> evaluation_timestamps)
	{
		run_result result{};

		for(suse::event next_event; std::cin>>next_event;++result.processed_events)
		{
			if(evaluation_timestamps.contains(next_event.timestamp))
				result.observations.push_back({selector.number_of_contained_complete_matches(),next_event.timestamp});

			const auto start = std::chrono::steady_clock::now();
				selector.process_event(next_event,strategy);
			const auto end = std::chrono::steady_clock::now();

			result.average_latency+=end-start;
			result.max_latency = std::max(result.max_latency,end-start);
			result.min_latency = std::min(result.min_latency,end-start);
		}
		result.average_latency/=result.processed_events;
		result.final_matches = selector.number_of_contained_complete_matches();
		result.final_partial_matches = selector.number_of_contained_partial_matches();

		result.detected_matches = selector.number_of_detected_complete_matches();
		result.detected_partial_matches = selector.number_of_detected_partial_matches();

		fmt::print("Partial Matches: {}, Complete Matches: {}\n",result.final_partial_matches,result.final_matches);
		return result;
	}

	void generate_report(const std::filesystem::path& path, nanoseconds init_time, nanoseconds runtime, const run_result& result)
	{
		std::ofstream out{path};
		fmt::print(out,"{{\n");
		fmt::print(out,"\t\"initialization_time_ns\": {},\n",init_time.count());
		fmt::print(out,"\t\"runtime_ns\": {},\n",runtime.count());
		fmt::print(out,"\t\"average_latency_ns\": {},\n",result.average_latency.count());
		fmt::print(out,"\t\"max_latency_ns\": {},\n",result.max_latency.count());
		fmt::print(out,"\t\"min_latency_ns\": {},\n",result.min_latency.count());
		fmt::print(out,"\t\"final_matches\": {},\n",result.final_matches);
		fmt::print(out,"\t\"final_partial_matches\": {},\n",result.final_partial_matches);
		fmt::print(out,"\t\"detected_matches\": {},\n",result.detected_matches);
		fmt::print(out,"\t\"detected_partial_matches\": {},\n",result.detected_partial_matches);
		fmt::print(out,"\t\"processed_events\": {},\n",result.processed_events);

		const auto observed_timestamps = std::views::transform(result.observations,[](const auto& o)
		{
			return o.timestamp;
		});

		const auto observed_matches = std::views::transform(result.observations,[](const auto& o)
		{
			return o.matches;
		});

		fmt::print(out,"\t\"observed_timestamps\": [{}],\n",fmt::join(observed_timestamps,", "));
		fmt::print(out,"\t\"observed_matches\": [{}]\n",fmt::join(observed_matches,", "));
		fmt::print(out,"}}\n");
	}
}

int main(int argc, char* argv[]) try
{
	cxxopts::Options options("summary_selector", "Transforms an eventstream to ");
	options.add_options()
		("query,q","Regex/Query to evaluate",cxxopts::value<std::string>())
		("strategy","Eviction strategy. Must be one of suse, fifo or random. Default is suse",cxxopts::value<std::string>()->default_value("suse"))
		("probabilities-file","For SuSe eviction strategy: file containing the probabilities for each character",cxxopts::value<std::string>())
		("summary-size,s","Size of the summary cache",cxxopts::value<std::size_t>())
		("time-window-size,t","Size of one time window",cxxopts::value<std::size_t>())
		("time-to-live","The maximum amount of time an event stays in the cache",cxxopts::value<std::size_t>()->default_value(std::to_string(std::numeric_limits<std::size_t>::max())))
		("evaluation-timestamps,e","Timestamps to evaluate at",cxxopts::value<std::vector<std::size_t>>())
		("output-nfa","File to write the graphviz-dot representation of the compiled NFA to",cxxopts::value<std::string>())
		("report,r","File to write results to",cxxopts::value<std::string>())
		("help,h","Display this help meassage");

	options.parse_positional("query");
	options.positional_help("query");

	const auto parsed_args = options.parse(argc,argv);

	if(parsed_args.count("help")>0 || argc<2)
	{
		fmt::print("{}",options.help());
		return 0;
	}

	for(auto required: {"query","summary-size","time-window-size"})
	{
		if(parsed_args.count(required)==0)
		{
			fmt::print(stderr,"{} is a required argument\n",required);
			return 1;
		}
	}

	const auto strategy = parsed_args["strategy"].template as<std::string>();
	const std::array<std::string_view,3> valid_strategies{"suse","fifo","random"};
	if(std::find(valid_strategies.begin(),valid_strategies.end(),strategy)==valid_strategies.end())
	{
		fmt::print(stderr,"{}",fmt::styled("Invalid strategy, aborting...\n",fmt::fg(fmt::color::red)));
		return 1;
	}

	const std::optional<std::filesystem::path> nfa_filename = parsed_args.count("output-nfa")?
		parsed_args["output-nfa"].as<std::string>():
		std::optional<std::filesystem::path>{};


	const auto query = parsed_args["query"].template as<std::string>();
	auto nfa = try_compile(query);
	if(!nfa)
	{
		fmt::print(stderr,"{}",fmt::styled("Invalid query, aborting...\n",fmt::fg(fmt::color::red)));
		return 1;
	}
	
	if(nfa_filename)
	{
		std::ofstream out{*nfa_filename};
		out<<*nfa;
	}

	const auto summary_size = parsed_args["summary-size"].template as<std::size_t>();
	const auto time_window_size = parsed_args["time-window-size"].template as<std::size_t>();
	const auto time_to_live = parsed_args["time-to-live"].template as<std::size_t>();
	const auto evaluation_timestamps = [&]() -> std::unordered_set<std::size_t>
	{
		if(parsed_args.count("evaluation-timestamps")==0)
			return {};
		
		const auto timestamps = parsed_args["evaluation-timestamps"].template as<std::vector<std::size_t>>();
		return {timestamps.begin(),timestamps.end()};
	}();

	const auto start_time = std::chrono::steady_clock::now();
	
	suse::summary_selector<counter_type> selector{query,summary_size,time_window_size,time_to_live};

	const auto measured_run = [&](auto& strategy)
	{
		const auto processing_start_time = std::chrono::steady_clock::now();
			const auto result = run(selector,strategy,evaluation_timestamps);
		const auto processing_end_time = std::chrono::steady_clock::now();	

		if(parsed_args.count("report")>0)
		{
			const auto filename = parsed_args["report"].template as<std::string>();
			generate_report(filename,processing_start_time-start_time,processing_end_time-processing_start_time,result);
		}
	};
	
	if(strategy=="fifo")
		measured_run(suse::eviction_strategies::fifo);
	else if(strategy=="random")
		measured_run(suse::eviction_strategies::random);
	else
	{
		const auto probabilities = parsed_args.count("probabilities-file")>0?
			load_probabilities(parsed_args["probabilities-file"].template as<std::string>()):
			generate_uniform_probabilities(*nfa); 
		suse::eviction_strategies::suse suse{selector,probabilities};

		measured_run(suse);
	}
	
	return 0;
}
catch(const cxxopts::exceptions::exception& e)
{
	fmt::print(stderr,"Error parsing arguments: {}\n", e.what());
	return 1;
}
