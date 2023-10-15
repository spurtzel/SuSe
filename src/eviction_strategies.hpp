#ifndef SUSE_EVICTION_STRATEGIES_HPP
#define SUSE_EVICTION_STRATEGIES_HPP

#include "execution_state_counter.hpp"
#include "event.hpp"
#include "summary_selector.hpp"

#include <optional>
#include <random>
#include <unordered_map>
#include <vector>

#include <cstddef>

namespace suse::eviction_strategies
{
	inline auto fifo = [](auto...) -> std::size_t
	{
		return 0;
	};

	inline auto random = []<typename counter_type>(const summary_selector<counter_type>& selector, const event&)
	{
		static std::mt19937 random_gen(std::random_device{}());
		std::uniform_int_distribution<std::size_t> dist(0,selector.cached_events().size()-1);

		return dist(random_gen);
	};

	template <typename counter_type, typename factor_type>
	class suse
	{
		using selector_type = summary_selector<counter_type>;
		using state_counter_type = execution_state_counter<counter_type>;
		
		public:
		explicit suse(const selector_type& selector, const std::unordered_map<char,factor_type>& probabilities);

		std::optional<std::size_t> select(const selector_type& selector, const event& event) const;

		private:
		struct state_change
		{
			std::vector<execution_state_counter<factor_type>> factors_per_state;
		};
		std::vector<state_change> expected_change_at_distance_; // name is bad...

		state_change determine_followup(const state_change& previous, const selector_type& selector,const std::unordered_map<char,factor_type>& probabilities) const;

		factor_type apply(const state_counter_type& counts, const execution_state_counter<factor_type>& factors) const;

		factor_type current_benefit(const selector_type& selector,const state_counter_type& counts) const;
		factor_type expected_future_benefit(const selector_type& selector,const state_counter_type& counts, std::size_t min_remaining, std::size_t max_remaining) const;
	};
}

#include "eviction_strategies_impl.hpp"

#endif
