#include "regex.hpp"

#include <doctest/doctest.h>

TEST_SUITE("suse::regex")
{
	TEST_CASE("empty")
	{
		const auto empty = suse::parse_regex("");
		
		CHECK(empty.check(""));
		CHECK(!empty.check("a"));
		CHECK(!empty.check("aa"));
	}

	TEST_CASE("single")
	{
		const auto single = suse::parse_regex("a");

		CHECK(single.check("a"));
		CHECK(!single.check("b"));
		CHECK(!single.check("ab"));
		CHECK(!single.check("aa"));
		CHECK(!single.check(""));
	}
	
	TEST_CASE("wildcard")
	{
		const auto single = suse::parse_regex(".");

		for(char c = 'a'; c<='z'; ++c)
		{
			CAPTURE(c);
			REQUIRE(single.check(std::string(1,c)));
		}
		CHECK(!single.check(""));
		CHECK(!single.check("ab"));
	}

	TEST_CASE("concatenation")
	{
		const auto concat= suse::parse_regex("ab");

		CHECK(concat.check("ab"));
		CHECK(!concat.check(""));
		CHECK(!concat.check("a"));
		CHECK(!concat.check("b"));
		CHECK(!concat.check("ba"));
		CHECK(!concat.check("aba"));
	}

	TEST_CASE("alternative")
	{
		const auto alt = suse::parse_regex("a|b");

		CHECK(alt.check("a"));
		CHECK(alt.check("b"));
		CHECK(!alt.check(""));
		CHECK(!alt.check("c"));
		CHECK(!alt.check("ab"));
		CHECK(!alt.check("ba"));
	}

	TEST_CASE("optional repetition")
	{
		const auto rep = suse::parse_regex("a*");

		std::string str = "";
		for(std::size_t i=0;i<100;++i,str+="a")
		{
			CAPTURE(str);
			REQUIRE(rep.check(str));
		}

		CHECK(!rep.check("b"));
		CHECK(!rep.check("ab"));
	}

	TEST_CASE("required repetition")
	{
		const auto rep = suse::parse_regex("a+");

		std::string str = "a";
		for(std::size_t i=0;i<100;++i,str+="a")
		{
			CAPTURE(str);
			REQUIRE(rep.check(str));
		}

		CHECK(!rep.check(""));
		CHECK(!rep.check("b"));
		CHECK(!rep.check("ab"));
	}

	TEST_CASE("option")
	{
		const auto rep = suse::parse_regex("a?");

		CHECK(rep.check(""));
		CHECK(rep.check("a"));
		CHECK(!rep.check("b"));
		CHECK(!rep.check("aa"));
		CHECK(!rep.check("ab"));
	}
	
	TEST_CASE("grouping")
	{
		const auto rep = suse::parse_regex("a(b|c)d");

		CHECK(rep.check("abd"));
		CHECK(rep.check("acd"));
		
		CHECK(!rep.check("ad"));
		CHECK(!rep.check("abcd"));
		CHECK(!rep.check("b"));
		CHECK(!rep.check("ab"));
		CHECK(!rep.check("ac"));
		CHECK(!rep.check(""));
	}
	
	TEST_CASE("repeated grouping")
	{
		const auto rep = suse::parse_regex("a(b|c)*d");

		CHECK(rep.check("abd"));
		CHECK(rep.check("acd"));	
		CHECK(rep.check("ad"));
		CHECK(rep.check("abcd"));
		CHECK(rep.check("acbd"));
		CHECK(rep.check("acbbbcd"));

		CHECK(!rep.check("b"));
		CHECK(!rep.check("ab"));
		CHECK(!rep.check("ac"));
		CHECK(!rep.check(""));
	}
	
	TEST_CASE("others")
	{
		const auto rep = suse::parse_regex("a*b+(c|d)");
		CHECK(rep.check("abc"));
		CHECK(rep.check("bc"));
		CHECK(rep.check("abd"));
		CHECK(rep.check("bd"));
		CHECK(rep.check("bbbd"));

		CHECK(!rep.check("ab"));
	}
}
