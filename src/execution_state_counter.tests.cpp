#include "execution_state_counter.hpp"

#include "regex.hpp"

#include <boost/multiprecision/cpp_int.hpp>
#include <boost/multiprecision/cpp_bin_float.hpp>

#include <doctest/doctest.h>

TEST_SUITE("suse::execution_state_counter")
{
	TEST_CASE("advance check")
	{
		const auto sample = suse::parse_regex("a(b|c)d?e");

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

		CHECK(sample.check("")==counter_check(""));
		CHECK(sample.check("abe")==counter_check("abe"));
		CHECK(sample.check("ace")==counter_check("ace"));
		CHECK(sample.check("abde")==counter_check("abde"));
		CHECK(sample.check("acde")==counter_check("acde"));
		CHECK(sample.check("ade")==counter_check("ade"));
	}

	TEST_CASE("advance edgelist check")
	{
		const auto sample = suse::parse_regex("a(b|c)d?e");
		const auto edges = suse::compute_edges_per_character(sample); 

		const auto counter_check = [&](std::string_view input)
		{
			auto counter = suse::execution_state_counter<int>(sample.number_of_states());
			counter[sample.initial_state_id()] = 1;

			for(auto c: input)
				counter = advance(counter,edges,c);

			for(std::size_t i=0;i<sample.number_of_states();++i)
			{
				if(sample.states()[i].is_final && counter[i]>0)
					return true;
			}

			return false;
		};

		CHECK(sample.check("")==counter_check(""));
		CHECK(sample.check("abe")==counter_check("abe"));
		CHECK(sample.check("ace")==counter_check("ace"));
		CHECK(sample.check("abde")==counter_check("abde"));
		CHECK(sample.check("acde")==counter_check("acde"));
		CHECK(sample.check("ade")==counter_check("ade"));
	}
}
