#ifndef SUSE_NFA_HPP
#define SUSE_NFA_HPP

#include <algorithm>
#include <iostream>
#include <span>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <cstddef>

namespace suse
{
	struct state
	{
		std::unordered_map<char,std::unordered_set<std::size_t>> transitions;
		bool is_final;

		friend bool operator==(const state& lhs, const state& rhs)
		{
			return lhs.is_final==rhs.is_final && lhs.transitions==rhs.transitions;
		}
	};

	class nfa
	{
		public:
		static constexpr char wildcard_symbol = '\b'; // assignment of those symbols is arbitrary
		static constexpr char epsilon_symbol = '\0';  // it just has to be something that cannot appear in normal text

		static nfa singleton(char symbol);
	
		bool check(std::string_view word) const;
		
		std::size_t number_of_states() const { return states_.size(); }
		std::size_t initial_state_id() const { return initial_state_id_; }
		std::span<const state> states() const { return states_; }
	
		friend nfa union_automaton(nfa lhs, const nfa& rhs); // dislike the name, but union is a keyword
		friend nfa concatenate(nfa lhs, const nfa& rhs);
		friend nfa kleene(nfa to_close);
	
		private:
		std::size_t initial_state_id_ = 0;
		std::vector<state> states_;

		nfa() = default;
		
		void simplify();
		void eliminate_epsilon_transitions();
		void remove_unreachable_states();
		bool try_merge_redundant_states();

		void erase_some(std::vector<bool> should_erase);

		friend std::ostream& operator<<(std::ostream& out, const nfa& automaton);
	};
}

#endif
