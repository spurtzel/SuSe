#include "edgelist.hpp"
#include "execution_state_counter.hpp"
#include "regex.hpp"

#include <boost/multiprecision/cpp_int.hpp>

#include <doctest/doctest.h>

#include <nanobench.h>

TEST_SUITE("suse::execution_state_counter")
{
	TEST_CASE("check vs counter_check")
	{
		const auto sample = suse::parse_regex("(a|b)(b|c)(c|d)e?f?gh+|(a|b)(b|c)(c|d)e?f?gj+");

		const auto counter_check = [&](std::string_view input)
		{
			auto counter = suse::execution_state_counter<int>(sample.number_of_states());
			counter[sample.initial_state_id()] = 1;

			for(auto c: input)
				counter = advance(counter,sample,c);

			for(std::size_t i=0;i<sample.number_of_states();++i)
			{
				if(sample.states()[i].is_final && counter[i]>0)
					return true;
			}

			return false;
		};

		auto b = ankerl::nanobench::Bench();
		b.relative(true);

		const std::string input = "abdefg" + std::string(1000,'h');
		b.run("nfa.check", [&]()
		{
			ankerl::nanobench::doNotOptimizeAway(sample.check(input)); 
		});

		b.run("advance execution_state_counter check", [&]()
		{
			ankerl::nanobench::doNotOptimizeAway(counter_check(input)); 
		});
	}
	
	TEST_CASE("per-state-transitions vs edge-list")
	{
		const auto sample = suse::parse_regex("(a|b)(b|c)(c|d)e?f?gh+|(a|b)(b|c)(c|d)e?f?gj+");

		const auto counter_check = [&](std::string_view input)
		{
			auto counter = suse::execution_state_counter<int>(sample.number_of_states());
			counter[sample.initial_state_id()] = 1;

			for(auto c: input)
				counter = advance(counter,sample,c);

			for(std::size_t i=0;i<sample.number_of_states();++i)
			{
				if(sample.states()[i].is_final && counter[i]>0)
					return true;
			}

			return false;
		};

		auto edgelist = suse::compute_edges_per_character(sample) ;

		const auto counter_check_edgelist = [&](std::string_view input)
		{
			auto counter = suse::execution_state_counter<int>(sample.number_of_states());
			counter[sample.initial_state_id()] = 1;

			for(auto c: input)
				counter = advance(counter,edgelist,c);

			for(std::size_t i=0;i<sample.number_of_states();++i)
			{
				if(sample.states()[i].is_final && counter[i]>0)
					return true;
			}

			return false;
		};

		auto b = ankerl::nanobench::Bench();
		b.relative(true);

		const std::string input = "abdefg" + std::string(1000,'h');
		b.run("advance", [&]()
		{
			ankerl::nanobench::doNotOptimizeAway(counter_check(input)); 
		});

		b.run("advance edgelist", [&]()
		{
			ankerl::nanobench::doNotOptimizeAway(counter_check_edgelist(input)); 
		});
	}
}
