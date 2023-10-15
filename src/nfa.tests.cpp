#include "nfa.hpp"

#include <doctest/doctest.h>

TEST_SUITE("suse::nfa")
{
	TEST_CASE("singleton")
	{
		const auto single = suse::nfa::singleton('a');
		
		CHECK(single.check("a"));
		CHECK(!single.check(""));
		CHECK(!single.check("b"));
		CHECK(!single.check("aa"));
	}

	TEST_CASE("union_automaton")
	{
		const auto a = suse::nfa::singleton('a');
		const auto b = suse::nfa::singleton('b');
		const auto a_or_b = union_automaton(a, b); 
		
		CHECK(a_or_b .check("a"));
		CHECK(a_or_b .check("b"));
		CHECK(!a_or_b .check("c"));
		CHECK(!a_or_b .check(""));
		CHECK(!a_or_b .check("ab"));
		CHECK(!a_or_b .check("ba"));
	}

	TEST_CASE("concatenate")
	{
		const auto a = suse::nfa::singleton('a');
		const auto b = suse::nfa::singleton('b');
		const auto ab = concatenate(a, b);
		
		CHECK(!ab.check("a"));
		CHECK(!ab.check("b"));
		CHECK(!ab.check("c"));
		CHECK(!ab.check(""));
		CHECK(ab.check("ab"));
		CHECK(!ab.check("ba"));
		CHECK(!ab.check("abc"));
	}

	TEST_CASE("kleene")
	{
		const auto a = suse::nfa::singleton('a');
		const auto b = suse::nfa::singleton('b');
		const auto ab = concatenate(a, b);
		const auto abstar = kleene(ab);
		
		CHECK(!abstar.check("a"));
		CHECK(!abstar.check("b"));
		CHECK(!abstar.check("c"));
		CHECK(!abstar.check("ba"));
		CHECK(!abstar.check("abc"));

		CHECK(abstar.check("ab"));

		std::string input = "";
		for(std::size_t i=0;i<100;++i, input+="ab")
		{
			CAPTURE(input);
			REQUIRE(abstar.check(input));
		}
	}

	TEST_CASE("wildcard")
	{
		const auto any = suse::nfa::singleton(suse::nfa::wildcard_symbol);
		
		CHECK(any.check("a"));
		CHECK(any.check("b"));
		CHECK(any.check("c"));
		CHECK(!any.check(""));
		CHECK(!any.check("ab"));
	}

	TEST_CASE("double kleene")
	{
		const auto a = suse::nfa::singleton('A');
		const auto astar = kleene(a);
		auto astarstar = kleene(astar); 

		std::string input = "";
		for(std::size_t i=0;i<100;++i, input+="A")
		{
			CAPTURE(input);
			REQUIRE(astarstar.check(input));
		}
		input+="BA";
		CAPTURE(input);
		CHECK(!astar.check(input));
	}
}
