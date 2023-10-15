#ifndef SUSE_EDGELIST_HPP
#define SUSE_EDGELIST_HPP

#include "nfa.hpp"

#include <array>
#include <vector>

#include <cstddef>

namespace suse
{
	struct edge
	{
		std::size_t from, to;

		friend constexpr auto operator<=>(const edge&, const edge&) = default;
	};

	class edgelist
	{
		public:
		friend edgelist compute_edges_per_character(const nfa& automaton);

		std::span<const edge> edges_for(char symbol) const;
		
		private:
		struct range
		{
			std::size_t start = 0, size = 0;
			
			friend constexpr auto operator<=>(const range&, const range&) = default;
		};
		std::array<range,256> character_to_range_;
		
		std::vector<edge> edges_;

		friend bool operator<=>(const edgelist&, const edgelist&) = default;
	};

	edgelist compute_edges_per_character(const nfa& automaton);
}

#endif
