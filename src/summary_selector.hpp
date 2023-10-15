#ifndef SUSE_SUMMARY_SELECTOR_HPP
#define SUSE_SUMMARY_SELECTOR_HPP

#include "edgelist.hpp"
#include "event.hpp"
#include "execution_state_counter.hpp"
#include "nfa.hpp"
#include "ring_buffer.hpp"

#include <concepts>
#include <limits>
#include <optional>
#include <span>
#include <string_view>
#include <unordered_map>
#include <vector>

#include <cstddef>

namespace suse
{
	template <typename T, typename cache_type>
	concept callable_eviction_strategy = requires(const T strategy, const cache_type cache, const event e)
	{
		{ strategy(cache,e) } -> std::convertible_to<std::optional<std::size_t>>;
	};

	template <typename T, typename cache_type>
	concept eviction_strategy_object = requires(const T strategy, const cache_type cache, const event e)
	{
		{ strategy.select(cache,e) } -> std::convertible_to<std::optional<std::size_t>>;
	};

	template <typename T, typename cache_type>
	concept eviction_strategy =  callable_eviction_strategy<T,cache_type> || eviction_strategy_object<T,cache_type>; 

	template <typename counter_type> 
	class summary_selector
	{
		public:
		summary_selector(std::string_view query, std::size_t summary_size, std::size_t time_window_size, std::size_t time_to_live = std::numeric_limits<std::size_t>::max());

		template <eviction_strategy<summary_selector> strategy_type>
		void process_event(const event& new_event, const strategy_type& strategy);
		void process_event(const event& new_event);

		void remove_event(std::size_t cache_index);

		auto cached_events() const { return std::span{cache_.begin(),cache_.end()}; }
		const auto& active_window() const { return active_window_; }
		const auto& total_counts() const { return total_counter_; }
		const auto& active_counts() const { return active_window_.total_counter; }

		auto current_time() const { return current_time_; }

		counter_type number_of_contained_complete_matches() const;
		counter_type number_of_contained_partial_matches() const;
		
		counter_type number_of_detected_complete_matches() const;
		counter_type number_of_detected_partial_matches() const;

		counter_type number_of_complete_matches(const execution_state_counter<counter_type>& counters) const;
		counter_type number_of_partial_matches(const execution_state_counter<counter_type>& counters) const;

		const auto& automaton() const { return automaton_; }
		auto time_window_size() const { return active_window_.per_event_counters.capacity(); }

		private:
		nfa automaton_;
		edgelist per_character_edges_;
		std::size_t time_to_live_;

		struct cache_entry
		{
			event cached_event;
			execution_state_counter<counter_type> state_counter;

			friend auto operator<=>(const cache_entry&, const cache_entry&) = default;
		};
		std::vector<cache_entry> cache_;

		struct window_info
		{
			execution_state_counter<counter_type> total_counter;
			suse::ring_buffer<execution_state_counter<counter_type>> per_event_counters;
			std::size_t start_idx;

			friend auto operator<=>(const window_info&, const window_info&) = default;
		};
		
		execution_state_counter<counter_type> total_counter_, total_detected_counter_;
		window_info active_window_;

		std::size_t current_time_{0};

		void add_event(const event& new_event);

		void purge_expired();

		void update_window(window_info& window, std::size_t timestamp);
		void replay_time_window(window_info& window) const;
		void replay_time_window(window_info& window, std::span<const cache_entry> events) const;

		void replay_affected_range(std::size_t removed_idx, std::size_t removed_timestamp);

		auto create_window_info(std::size_t capacity) const;
		void reset_counters(window_info& window) const;

		std::size_t timestamp_at(std::size_t cache_idx) const;
		bool in_shared_window(std::size_t timestamp0, std::size_t timestamp1) const;

		template <typename T>
		friend bool operator==(const summary_selector<T>& lhs, const summary_selector<T>& rhs);
	};
}

#include "summary_selector_impl.hpp"

#endif
