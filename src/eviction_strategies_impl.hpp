/*
	Never include directly!
	This is included by eviction_strategies.hpp and only exists to split
	interface and implementation despite the template.
*/

#include <algorithm>

#include <cstddef>

namespace suse::eviction_strategies
{

template <typename counter_type, typename factor_type>
suse<counter_type,factor_type>::suse(const selector_type& selector,const std::unordered_map<char,factor_type>& probabilities)
{
	state_change identity_factors{};
	for(std::size_t state_id = 0; state_id<selector.automaton().number_of_states(); ++state_id)
	{
		execution_state_counter<factor_type> factors{selector.automaton().number_of_states()};
		factors[state_id] = factor_type{1};
		identity_factors.factors_per_state.push_back(std::move(factors));
	}
	expected_change_at_distance_.push_back(std::move(identity_factors));

	for(std::size_t i=0;i<selector.time_window_size();++i)
	{
		auto followup = determine_followup(expected_change_at_distance_.back(),selector,probabilities);
		expected_change_at_distance_.push_back(std::move(followup));
	}
}

template <typename counter_type, typename factor_type>
auto suse<counter_type,factor_type>::determine_followup(const state_change& previous, const selector_type& selector,const std::unordered_map<char,factor_type>& probabilities) const -> state_change
{
	const auto& automaton = selector.automaton();
	
	auto next = previous;
	for(std::size_t source_id = 0; source_id<automaton.number_of_states(); ++source_id)
	{
		for(const auto& [symbol,destination_ids]: automaton.states()[source_id].transitions)
		{
			if(auto it=probabilities.find(symbol); it!=probabilities.end())
			{
				for(auto destination_id: destination_ids)
					next.factors_per_state[destination_id] += it->second * previous.factors_per_state[source_id];
			}
		}
	}

	return next;
}

template <typename counter_type, typename factor_type>
std::optional<std::size_t> suse<counter_type,factor_type>::select(const selector_type& selector, const event& new_event) const
{
	const auto is_initiator = [&](char symbol)
	{
		const auto& automaton = selector.automaton();
		const auto& initial_state = automaton.states()[automaton.initial_state_id()];
		
		return initial_state.transitions.count(nfa::wildcard_symbol)>0 || initial_state.transitions.count(symbol)>0;
	};
	
	const auto& events = selector.cached_events();
	const auto& window = selector.active_window();
	
	std::size_t oldest_initiator = 0, newest_initiator = 0;

	std::optional<factor_type> lowest_benefit = std::nullopt;
	std::size_t lowest_idx = 0;
	for(std::size_t idx=0;idx<events.size();++idx)
	{
		const auto& event = events[idx];
		if(idx>=window.start_idx && is_initiator(event.cached_event.type))
		{
			oldest_initiator = oldest_initiator==0?idx:oldest_initiator;
			newest_initiator = idx;
		}

		const auto min_time_used = selector.current_time() - events[newest_initiator].cached_event.timestamp;
		const auto max_time_used = selector.current_time() - events[oldest_initiator].cached_event.timestamp;
		const auto min_time_left = max_time_used>selector.time_window_size()?0:selector.time_window_size()-max_time_used;
		const auto max_time_left = min_time_used>selector.time_window_size()?0:selector.time_window_size()-min_time_used;

		auto benefit = current_benefit(selector,event.state_counter);
		if(idx>=window.start_idx)
			benefit += expected_future_benefit(selector,window.per_event_counters[idx-window.start_idx],min_time_left,max_time_left);

		if(!lowest_benefit || benefit<*lowest_benefit)
		{
			lowest_benefit = std::move(benefit);
			lowest_idx = idx;
		}
	}
	
	const auto new_counters = advance(selector.active_counts(),selector.automaton(), new_event.type);
	auto newest_init_time = is_initiator(new_event.type)?new_event.timestamp:events[newest_initiator].cached_event.timestamp;
	const auto min_time_used = selector.current_time() - newest_init_time;
	const auto max_time_used = selector.current_time() - events[oldest_initiator].cached_event.timestamp;
	const auto min_time_left = max_time_used>selector.time_window_size()?0:selector.time_window_size()-max_time_used;
	const auto max_time_left = min_time_used>selector.time_window_size()?0:selector.time_window_size()-min_time_used;

	const auto benefit_if_added = current_benefit(selector,new_counters) + expected_future_benefit(selector,new_counters,min_time_left, max_time_left);
	if(benefit_if_added>*lowest_benefit)
		return lowest_idx;

	return std::nullopt;
}

template <typename counter_type, typename factor_type>
factor_type suse<counter_type,factor_type>::apply(const state_counter_type& counts, const execution_state_counter<factor_type>& factors) const
{
	const auto multiply = [](const factor_type& factor, const counter_type& counter)
	{
		return factor*static_cast<factor_type>(counter);
	};

	return std::inner_product(factors.begin(),factors.end(),counts.begin(),factor_type{0},std::plus<>{},multiply);
}

template <typename counter_type, typename factor_type>
factor_type suse<counter_type,factor_type>::current_benefit(const selector_type& selector,const state_counter_type& counts) const
{
	factor_type sum{};
	for(std::size_t idx=0;idx<counts.size();++idx)
	{
		if(selector.automaton().states()[idx].is_final)
			sum += static_cast<factor_type>(counts[idx]);
	}
	return sum;
}

template <typename counter_type, typename factor_type>
factor_type suse<counter_type,factor_type>::expected_future_benefit(const selector_type& selector,const state_counter_type& counts, std::size_t min_remaining, std::size_t max_remaining) const
{
	const auto& min_factors = expected_change_at_distance_[min_remaining].factors_per_state;
	const auto& max_factors = expected_change_at_distance_[max_remaining].factors_per_state;
	
	factor_type sum{};
	for(std::size_t idx=0;idx<counts.size();++idx)
	{
		if(selector.automaton().states()[idx].is_final)
			sum += (apply(counts,min_factors[idx]) + apply(counts,max_factors[idx])) / static_cast<factor_type>(2);
	}
	return sum - current_benefit(selector,counts);
}

}
