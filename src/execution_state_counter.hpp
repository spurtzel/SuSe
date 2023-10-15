#ifndef SUSE_EXECUTION_STATE_COUNTER_HPP
#define SUSE_EXECUTION_STATE_COUNTER_HPP

#include "edgelist.hpp"
#include "nfa.hpp"

#include <type_traits>
#include <unordered_map>
#include <vector>

#include <cstddef>

namespace suse
{
	template <typename underlying_counter_type>
	struct execution_state_counter
	{
		public:
		explicit execution_state_counter(std::size_t number_of_states):
			counters_(number_of_states,0)
		{}

		std::size_t size() const { return counters_.size(); }

		underlying_counter_type& operator[](std::size_t idx) { return counters_[idx]; }
		const underlying_counter_type& operator[](std::size_t idx) const { return counters_[idx]; }

		auto begin() const { return counters_.begin(); }
		auto end() const { return counters_.end(); }

		auto begin() { return counters_.begin(); }
		auto end() { return counters_.end(); }

		execution_state_counter& operator+=(const execution_state_counter& other);
		execution_state_counter& operator-=(const execution_state_counter& other);
		execution_state_counter& operator*=(const underlying_counter_type& factor);

		friend execution_state_counter operator+(execution_state_counter lhs, const execution_state_counter& rhs)
		{
			return lhs+=rhs;
		}

		friend execution_state_counter operator-(execution_state_counter lhs, const execution_state_counter& rhs)
		{
			return lhs-=rhs;
		}

		friend execution_state_counter operator*(execution_state_counter lhs, const underlying_counter_type& rhs)
		{
			return lhs*=rhs;
		}

		friend execution_state_counter operator*(const underlying_counter_type lhs, execution_state_counter rhs)
		{
			return rhs*=lhs;
		}

		friend auto operator<=>(const execution_state_counter&, const execution_state_counter&) = default;

		private:
		std::vector<underlying_counter_type> counters_;
	};

	template <typename underlying_counter_type>
	execution_state_counter<underlying_counter_type> advance(const execution_state_counter<underlying_counter_type>& counter, const nfa& automaton, char symbol);

	template <typename underlying_counter_type>
	execution_state_counter<underlying_counter_type> advance(const execution_state_counter<underlying_counter_type>& counter, const edgelist& per_character_edges, char symbol);
}

#include "execution_state_counter_impl.hpp"

#endif
