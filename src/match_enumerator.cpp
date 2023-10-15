#include "event.hpp"
#include "nfa.hpp"
#include "regex.hpp"

#include <boost/multiprecision/cpp_int.hpp>

#include <cxxopts.hpp>

#include <fmt/color.h>
#include <fmt/format.h>
#include <fmt/ostream.h>
#include <fmt/chrono.h>

#include <deque>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

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
}

using counter_type = boost::multiprecision::uint256_t;
template <> struct fmt::formatter<counter_type>: fmt::ostream_formatter {};

int main(int argc, char* argv[]) try
{
	cxxopts::Options options("match_enumerator", "Enumerates all matches in a stream");
	options.add_options()
		("query,q","Regex/Query to evaluate",cxxopts::value<std::string>())
		("count,c","Count only, don't output matches")
		("help,h","Display this help meassage");

	options.parse_positional("query");
	options.positional_help("query");

	const auto parsed_args = options.parse(argc,argv);

	if(parsed_args.count("help")>0 || argc<2)
	{
		fmt::print("{}",options.help());
		return 0;
	}

	for(auto required: {"query"})
	{
		if(parsed_args.count(required)==0)
		{
			fmt::print(stderr,"{} is a required argument\n",required);
			return 1;
		}
	}

	const auto query = parsed_args["query"].template as<std::string>();
	auto nfa = try_compile(query);
	if(!nfa)
	{
		fmt::print(stderr,"{}",fmt::styled("Invalid query, aborting...\n",fmt::fg(fmt::color::red)));
		return 1;
	}
	
	struct partial_match
	{
		std::size_t event_index, previous_state_id, previous_state_size;
	};
	
	std::vector<std::vector<std::optional<partial_match>>> partial_matches_per_state(nfa->number_of_states());
	std::vector<std::size_t> number_of_partial_matches_per_state(nfa->number_of_states(),0);
	partial_matches_per_state[nfa->initial_state_id()].push_back(std::nullopt);
	number_of_partial_matches_per_state[nfa->initial_state_id()] = 1;

	std::vector<suse::event> events;
	counter_type number_of_matches = 0;

	const auto enumerate_from = [&](std::size_t state_id, std::size_t number_of_preceding_partial_matches, std::vector<std::size_t>& relevant_events, auto rec) -> void
	{
		for(std::size_t match_id = 0; match_id<number_of_preceding_partial_matches; ++match_id)
		{
			if(auto match = partial_matches_per_state[state_id][match_id]; match)
			{
				relevant_events.push_back(match->event_index);
					rec(match->previous_state_id,match->previous_state_size,relevant_events,rec);
				relevant_events.pop_back();
			}
			else
			{
				for(auto it=relevant_events.rbegin();it!=relevant_events.rend();++it)
					fmt::print("| {} at {} |",events[*it].type,events[*it].timestamp);
				
				fmt::print("\n");
			}
		}
	};

	const auto count_from = [&](std::size_t state_id, std::size_t number_of_preceding_partial_matches, auto rec) -> void
	{
		for(std::size_t match_id = 0; match_id<number_of_preceding_partial_matches; ++match_id)
		{
			if(auto match = partial_matches_per_state[state_id][match_id]; match)
				rec(match->previous_state_id,match->previous_state_size,rec);
			else
				++number_of_matches;
		}
	};

	const auto add_followups = [&](std::size_t source_state_id, std::size_t target_state_id)
	{
		const auto number_of_old_matches = number_of_partial_matches_per_state[source_state_id];
		if(nfa->states()[target_state_id].is_final)
		{
			if(parsed_args.count("count")>0)
				count_from(source_state_id,number_of_old_matches,count_from);
			else
			{
				std::vector<std::size_t> relevant_events{events.size()-1};
				enumerate_from(source_state_id,number_of_old_matches,relevant_events,enumerate_from);
			}
		}

		if(!nfa->states()[target_state_id].transitions.empty())
			partial_matches_per_state[target_state_id].push_back(partial_match{events.size()-1,source_state_id,number_of_old_matches});
	};

	const auto advance_all = [&](std::size_t state_id, char type)
	{
		const auto& transitions = nfa->states()[state_id].transitions;
		if(auto it = transitions.find(type); it!=transitions.end())
			for(const auto& target: it->second)
				add_followups(state_id,target);

		if(auto it = transitions.find(suse::nfa::wildcard_symbol); it!=transitions.end())
			for(const auto& target: it->second)
				add_followups(state_id,target);
	};

	for(suse::event next_event; std::cin>>next_event;)
	{
		events.push_back(next_event);

		for(std::size_t state_id = 0; state_id<nfa->number_of_states(); ++state_id)
			advance_all(state_id, next_event.type);

		for(std::size_t state_id = 0; state_id<nfa->number_of_states(); ++state_id)
			number_of_partial_matches_per_state[state_id] = partial_matches_per_state[state_id].size();
	}

	if(parsed_args.count("count")>0)
		fmt::print("{}\n",number_of_matches);

	return 0;
}
catch(const cxxopts::exceptions::exception& e)
{
	fmt::print(stderr,"Error parsing arguments: {}\n", e.what());
	return 1;
}
