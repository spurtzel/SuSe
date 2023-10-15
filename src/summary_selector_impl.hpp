/*
	Never include directly!
	This is included by summary_selector.hpp and only exists to split
	interface and implementation despite the template.
*/

#include "regex.hpp"

#include <cassert>

namespace suse
{

template <typename counter_type>
summary_selector<counter_type>::summary_selector(std::string_view query, std::size_t summary_size, std::size_t time_window_size, std::size_t time_to_live):
	automaton_{parse_regex(query)},
	per_character_edges_{compute_edges_per_character(automaton_)},
	time_to_live_{time_to_live},
	cache_{},
	total_counter_{automaton_.number_of_states()},
	total_detected_counter_{automaton_.number_of_states()},
	active_window_{create_window_info(time_window_size)}
{
	cache_.reserve(summary_size);
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_contained_complete_matches() const
{
	return number_of_complete_matches(total_counter_);
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_contained_partial_matches() const
{
	return number_of_partial_matches(total_counter_);
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_detected_complete_matches() const
{
	return number_of_complete_matches(total_detected_counter_);
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_detected_partial_matches() const
{
	return number_of_partial_matches(total_detected_counter_);
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_complete_matches(const execution_state_counter<counter_type>& counter) const
{
	assert(counter.size()==automaton.number_of_states());
	
	counter_type sum{0};
	for(std::size_t i=0;i<counter.size();++i)
	{
		if(automaton_.states()[i].is_final)
			sum+=counter[i];
	}

	return sum;
}

template <typename counter_type>
counter_type summary_selector<counter_type>::number_of_partial_matches(const execution_state_counter<counter_type>& counter) const
{
	assert(counter.size()==automaton.number_of_states());
	
	counter_type sum{0};
	for(std::size_t i=0;i<counter.size();++i)
	{
		if(!automaton_.states()[i].is_final)
			sum+=counter[i];
	}

	return sum;
}

template <typename counter_type>
template <eviction_strategy<summary_selector<counter_type>> strategy_type>
void summary_selector<counter_type>::process_event(const event& new_event, const strategy_type& strategy)
{
	current_time_ = new_event.timestamp;
	update_window(active_window_,new_event.timestamp);
	purge_expired();

	const auto select_idx_to_evict = [&]() -> std::optional<std::size_t>
	{
		if constexpr(callable_eviction_strategy<strategy_type,summary_selector>)
			return strategy(*this,new_event);
		else
			return strategy.select(*this,new_event);
	};

	if(cache_.size()==cache_.capacity())
	{
		if(auto to_remove = select_idx_to_evict(); to_remove)
			remove_event(*to_remove);
	}

	if(cache_.size()<cache_.capacity())
		add_event(new_event);
}

template <typename counter_type>
void summary_selector<counter_type>::process_event(const event& new_event)
{
	process_event(new_event,[](auto...){ return std::nullopt; });
}

template <typename counter_type>
void summary_selector<counter_type>::remove_event(std::size_t cache_index)
{
	assert(cache_index<cache_.size());
	
	total_counter_-=cache_[cache_index].state_counter;
	const auto removed_timestamp = timestamp_at(cache_index);
	if(cache_index<active_window_.start_idx)
		--active_window_.start_idx;

	cache_.erase(cache_.begin()+cache_index);

	if(cache_.empty())
	{
		active_window_.start_idx = 0;
		reset_counters(active_window_);
		return;
	}

	replay_affected_range(cache_index, removed_timestamp);
	if(in_shared_window(current_time_,removed_timestamp))
		replay_time_window(active_window_,std::span{cache_.begin()+active_window_.start_idx,cache_.end()});
}

template <typename counter_type>
void summary_selector<counter_type>::replay_affected_range(std::size_t removed_idx, std::size_t removed_timestamp)
{
	auto replay_start_idx = removed_idx<time_window_size()?0:removed_idx-time_window_size();
	while(replay_start_idx<cache_.size() && !in_shared_window(removed_timestamp,timestamp_at(replay_start_idx)))
		++replay_start_idx;

	const auto replay_start_timestamp = timestamp_at(replay_start_idx);

	auto time_window_replay_start_idx = replay_start_idx<time_window_size()?0:replay_start_idx-time_window_size();
	while(time_window_replay_start_idx<cache_.size() && !in_shared_window(replay_start_timestamp,timestamp_at(time_window_replay_start_idx)))
		++time_window_replay_start_idx;

	auto replay_window = create_window_info(time_window_size());
	replay_window.start_idx = time_window_replay_start_idx;
	const auto relevant_prefix = std::span{cache_.begin()+replay_window.start_idx,cache_.begin()+replay_start_idx};
	replay_time_window(replay_window,relevant_prefix);

	const auto is_relevant = [&](std::size_t idx)
	{
		const auto affected = in_shared_window(removed_timestamp,timestamp_at(idx));
		const auto in_affecting_window = in_shared_window(removed_timestamp,timestamp_at(replay_window.start_idx));

		return affected || in_affecting_window;
	};
	
	for(std::size_t idx = replay_start_idx; idx<cache_.size() && is_relevant(idx); ++idx)
	{
		update_window(replay_window,timestamp_at(idx));
		
		auto global_counter_change = advance(replay_window.total_counter,per_character_edges_,cache_[idx].cached_event.type);
		replay_window.total_counter+=global_counter_change;

		const auto active_window_size = idx - replay_window.start_idx;
		for(std::size_t i=0; i<active_window_size;++i)
		{
			const auto cache_idx = replay_window.start_idx + i;
			
			const auto local_change = advance(replay_window.per_event_counters[i],per_character_edges_,cache_[idx].cached_event.type);
			if(cache_idx>=replay_start_idx && in_shared_window(removed_timestamp,timestamp_at(cache_idx)))
				cache_[cache_idx].state_counter+=local_change;
			replay_window.per_event_counters[i]+=local_change;
		}
		
		replay_window.per_event_counters.push_back(global_counter_change);
		if(in_shared_window(removed_timestamp,timestamp_at(idx)))
			cache_[idx].state_counter = std::move(global_counter_change);
	}
}

template <typename counter_type>
void summary_selector<counter_type>::add_event(const event& new_event)
{
	auto global_counter_change = advance(active_window_.total_counter,per_character_edges_,new_event.type);
	active_window_.total_counter+=global_counter_change;
	total_counter_+=global_counter_change;
	total_detected_counter_+=global_counter_change;

	const auto active_window_size = cache_.size() - active_window_.start_idx;
	for(std::size_t i=0; i<active_window_size;++i)
	{
		const auto cache_idx = active_window_.start_idx + i;
		
		const auto local_change = advance(active_window_.per_event_counters[i],per_character_edges_,new_event.type);
		cache_[cache_idx].state_counter+=local_change;
		active_window_.per_event_counters[i]+=local_change;
	}
	
	active_window_.per_event_counters.push_back(global_counter_change);
	cache_.emplace_back(new_event,std::move(global_counter_change));
}

template <typename counter_type>
void summary_selector<counter_type>::purge_expired()
{
	std::size_t purge_until = 0;
	while(purge_until<cache_.size() && current_time()-cache_[purge_until].cached_event.timestamp>time_to_live_)
	{
		total_counter_-=cache_[purge_until].state_counter;
		const auto removed_timestamp = timestamp_at(purge_until);
		cache_[purge_until].cached_event.timestamp = std::numeric_limits<std::size_t>::max(); //dirty hack to make the replay ignore this event
		std::fill(cache_[purge_until].state_counter.begin(),cache_[purge_until].state_counter.end(),0);
		replay_affected_range(purge_until+1, removed_timestamp);
		++purge_until;
	}

	if(purge_until==0)
		return;
	
	cache_.erase(cache_.begin(),cache_.begin()+purge_until);

	if(cache_.empty())
	{
		active_window_.start_idx = 0;
		reset_counters(active_window_);
		return;
	}

	if(purge_until<active_window_.start_idx)
		active_window_.start_idx-=purge_until;
	else
	{
		active_window_.start_idx = cache_.size()>time_window_size()?cache_.size()-time_window_size():0;
		replay_time_window(active_window_,std::span{cache_.begin()+active_window_.start_idx,cache_.end()});
	}
}

template <typename counter_type>
void summary_selector<counter_type>::update_window(window_info& window, std::size_t timestamp)
{
	const auto& initial_state = automaton_.states()[automaton_.initial_state_id()];

	bool removed_initiator = false;
	while(!window.per_event_counters.empty() && !in_shared_window(timestamp,timestamp_at(window.start_idx)))
	{
		const auto type = cache_[window.start_idx++].cached_event.type;
		removed_initiator |= initial_state.transitions.contains(type) || initial_state.transitions.contains(nfa::wildcard_symbol);
		window.per_event_counters.pop_front();
	}

	if(removed_initiator)
		replay_time_window(window);
}

template <typename counter_type>
void summary_selector<counter_type>::replay_time_window(window_info& window) const
{
	replay_time_window(window,std::span{cache_.begin()+window.start_idx,window.per_event_counters.size()});
}

template <typename counter_type>
void summary_selector<counter_type>::replay_time_window(window_info& window, std::span<const cache_entry> events) const
{
	reset_counters(window);

	for(std::size_t i=0;i<events.size();++i)
	{
		const auto to_readd = events[i].cached_event.type;
		auto global_counter_change = advance(window.total_counter,per_character_edges_,to_readd);
		window.total_counter+=global_counter_change;
		for(std::size_t j=0;j<i;++j)
		{
			const auto local_change = advance(window.per_event_counters[j],per_character_edges_,to_readd);
			window.per_event_counters[j]+=local_change;
		}
		window.per_event_counters.push_back(std::move(global_counter_change));
	}
}

template <typename counter_type>
auto summary_selector<counter_type>::create_window_info(std::size_t window_size) const
{
	window_info wnd
	{
		execution_state_counter<counter_type>{automaton_.number_of_states()},
		ring_buffer<execution_state_counter<counter_type>>{window_size,execution_state_counter<counter_type>{automaton_.number_of_states()}},
		0
	};

	reset_counters(wnd);
	return wnd;
}

template <typename counter_type>
void summary_selector<counter_type>::reset_counters(window_info& window) const
{
	window.total_counter*=0; // performance!
	window.total_counter[automaton_.initial_state_id()] = 1;
	window.per_event_counters.clear();
}

template <typename counter_type>
std::size_t summary_selector<counter_type>::timestamp_at(std::size_t cache_idx) const
{
	assert(cache_idx<cache_.size());
	
	return cache_[cache_idx].cached_event.timestamp;
}

template <typename counter_type>
bool summary_selector<counter_type>::in_shared_window(std::size_t timestamp0, std::size_t timestamp1) const
{
	const auto time_window_size = active_window_.per_event_counters.capacity();

	if(timestamp1>timestamp0)
		std::swap(timestamp0,timestamp1);

	return timestamp0-timestamp1<=time_window_size;
}

template <typename counter_type>
bool operator==(const summary_selector<counter_type>& lhs, const summary_selector<counter_type>& rhs)
{
	if(lhs.per_character_edges_!=rhs.per_character_edges_) return false;
	if(lhs.cache_!=rhs.cache_) return false;
	if(lhs.total_counter_!=rhs.total_counter_) return false;
	if(lhs.current_time_!=rhs.current_time_) return false;

	return lhs.active_window_==rhs.active_window_;
}

}
