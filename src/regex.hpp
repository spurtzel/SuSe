#ifndef SUSE_REGEX_HPP
#define SUSE_REGEX_HPP

#include "nfa.hpp"

#include <stdexcept>
#include <string_view>

namespace suse
{
	struct regex_parse_error: std::runtime_error
	{
		regex_parse_error(const std::string& description, std::size_t location):
			std::runtime_error{description},
			location{location}
		{}
			
		std::size_t location;
	};
	
	nfa parse_regex(std::string_view input);
}

#endif
