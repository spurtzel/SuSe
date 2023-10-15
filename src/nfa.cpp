#include "nfa.hpp"

#include <numeric>
#include <string>

using namespace suse;

suse::nfa nfa::singleton(char symbol)
{
	nfa result;
	result.initial_state_id_ = 0;
	if(symbol!=epsilon_symbol)
		result.states_.push_back(state{{{symbol,{1}}},false});

	result.states_.push_back(state{{},true});
	return result;
}

bool nfa::check(std::string_view word) const
{
	std::unordered_set<std::size_t> current_state_ids{initial_state_id_};

	for(auto c: word)
	{
		std::unordered_set<std::size_t> next_state_ids;
		for(auto state_id: current_state_ids)
		{
			const auto& current_state = states_[state_id];
			if(auto it=current_state.transitions.find(c); it!=current_state.transitions.end())
				next_state_ids.insert(it->second.begin(),it->second.end());

			if(auto it=current_state.transitions.find(wildcard_symbol); it!=current_state.transitions.end())
				next_state_ids.insert(it->second.begin(),it->second.end());
		}
		current_state_ids = std::move(next_state_ids);
		
		if(current_state_ids.empty())
			return false;
	}

	return std::any_of(current_state_ids.begin(),current_state_ids.end(),[&](auto id)
	{
		return states_[id].is_final;
	});
}

void nfa::simplify()
{
	eliminate_epsilon_transitions();
	remove_unreachable_states();
	while(try_merge_redundant_states())
		/*intentionally blank*/;
}

void nfa::eliminate_epsilon_transitions()
{
	std::vector<std::unordered_set<std::size_t>> merged_per_state(states_.size());
	
	for(bool changed=true; changed;)
	{
		changed = false;
		for(std::size_t state_id=0; state_id<states_.size(); ++state_id)
		{
			auto& state = states_[state_id];
			if(auto it=state.transitions.find(epsilon_symbol); it!=state.transitions.end())
			{
				changed = true;
				auto& target_ids = it->second;
				for(auto to_merge_id: target_ids)
				{
					merged_per_state[state_id].insert(to_merge_id);
					if(to_merge_id==state_id)
						continue;

					state.is_final|=states_[to_merge_id].is_final;

					for(const auto& [symbol, targets]: states_[to_merge_id].transitions)
					{
						for(auto target: targets)
							state.transitions[symbol].insert(target);
					}
				}

				for(auto already_merged: merged_per_state[state_id])
					state.transitions[epsilon_symbol].erase(already_merged);

				if(state.transitions[epsilon_symbol].empty())
					state.transitions.erase(epsilon_symbol);
			}
		}
	}
}

void nfa::remove_unreachable_states()
{
	std::vector<bool> unreachable(states_.size(),true);
	unreachable[initial_state_id_] = false;

	for(std::size_t state_id=0; state_id<states_.size(); ++state_id)
	{
		for(const auto& [_,targets]: states_[state_id].transitions)
			for(auto target: targets)
				unreachable[target] = false;
	}

	erase_some(unreachable);
}

bool nfa::try_merge_redundant_states()
{
	std::vector<std::size_t> grouping(states_.size());
	std::iota(grouping.begin(),grouping.end(),std::size_t{0});

	const auto find_representative_state = [&](std::size_t state_id)
	{
		std::size_t representative = state_id;
		while(grouping[representative]!=representative)
			representative = grouping[representative];

		//compact:
		while(grouping[state_id]!=state_id)
		{
			const auto next = grouping[state_id];
			grouping[state_id] = representative;
			state_id = next;
		}

		return representative;
	};

	const auto merge_groups = [&](std::size_t state_id0, std::size_t state_id1)
	{
		state_id0 = find_representative_state(state_id0); 
		state_id1 = find_representative_state(state_id1);

		if(state_id0!=state_id1)
			grouping[state_id0] = state_id1;
	};

	bool any_merged = false;
	for(std::size_t state0_id=0;state0_id<states_.size();++state0_id)
	{
		for(std::size_t state1_id=state0_id+1;state1_id<states_.size();++state1_id)
		{
			if(states_[state0_id]==states_[state1_id])
			{
				merge_groups(state0_id,state1_id);
				any_merged = true;
			}
		}
	}

	std::vector<bool> should_erase(states_.size(),false);
	initial_state_id_ = find_representative_state(initial_state_id_); 
	for(std::size_t state_id=0;state_id<states_.size();++state_id)
	{
		if(auto rep = find_representative_state(state_id);rep!=state_id)
		{
			should_erase[state_id] = true;
			for(auto& state: states_)
			{
				for(auto& [_,transitions]: state.transitions)
				{
					if(transitions.erase(state_id)>0)
						transitions.insert(rep);
				}
			}
		}
	}
	erase_some(should_erase);

	return any_merged;
}

void nfa::erase_some(std::vector<bool> should_erase)
{
	const auto rename = [&](std::size_t old_id, std::size_t new_id)
	{
		should_erase[new_id] = should_erase[old_id];
		if(should_erase[old_id]) return;

		if(initial_state_id_==old_id)
			initial_state_id_ = new_id;

		for(auto& state: states_)
		{
			for(auto& [_,targets]: state.transitions)
			{
				if(targets.erase(old_id)>0)
					targets.insert(new_id);
			}
		}
	};

	for(std::size_t state_id=0; state_id<states_.size(); ++state_id)
	{
		if(should_erase[state_id])
		{
			rename(states_.size()-1,state_id);
			std::swap(states_[state_id],states_.back());
			states_.pop_back();
			--state_id;
		}
	}
}

namespace suse
{	
	// States are uniquely identified via their position in the states_ array.
	// As such, if two automatons are merged, all references have to be adjusted accordingly.

	nfa union_automaton(nfa lhs, const nfa& rhs)
	{
		const auto rhs_state_offset = lhs.states_.size();
		const auto lhs_initial_id = lhs.initial_state_id_;
		const auto rhs_initial_id = rhs.initial_state_id_ + rhs_state_offset;
		
		nfa result = std::move(lhs);
		result.states_.resize(result.states_.size()+rhs.states_.size());

		for(std::size_t i=0;i<rhs.states_.size();++i)
		{
			result.states_[rhs_state_offset+i].is_final = rhs.states_[i].is_final;
			for(auto& [symbol,targets]: rhs.states_[i].transitions)
			{
				for(auto& target: targets)
					result.states_[i+rhs_state_offset].transitions[symbol].insert(target+rhs_state_offset);
			}
		}

		state new_start;
		new_start.is_final = false;
		new_start.transitions[nfa::epsilon_symbol].insert(lhs_initial_id);
		new_start.transitions[nfa::epsilon_symbol].insert(rhs_initial_id);
		result.states_.push_back(std::move(new_start));
		result.initial_state_id_ = result.states_.size()-1;

		const auto new_end_id = result.states_.size();
		for(auto& state: result.states_)
		{
			if(state.is_final)
			{
				state.is_final = false;
				state.transitions[nfa::epsilon_symbol].insert(new_end_id);
			}
		}

		state new_end;
		new_end.is_final = true;
		result.states_.push_back(std::move(new_end));

		result.simplify();
		return result;
	}

	nfa concatenate(nfa lhs, const nfa& rhs)
	{
		const auto lhs_end = lhs.states_.size();
		const auto rhs_state_offset = lhs.states_.size();
		
		nfa result = std::move(lhs);
		result.states_.resize(result.states_.size()+rhs.states_.size());

		for(std::size_t i=0;i<rhs.states_.size();++i)
		{
			result.states_[rhs_state_offset+i].is_final = rhs.states_[i].is_final;
			for(auto& [symbol,targets]: rhs.states_[i].transitions)
			{
				for(auto& target: targets)
					result.states_[i+rhs_state_offset].transitions[symbol].insert(target+rhs_state_offset);
			}
		}

		const auto rhs_initial_id = rhs.initial_state_id_ + rhs_state_offset;
		for(std::size_t i=0;i<lhs_end;++i)
		{
			if(result.states_[i].is_final)
			{
				result.states_[i].is_final = false;
				result.states_[i].transitions[nfa::epsilon_symbol].insert(rhs_initial_id);
			}
		}

		result.simplify();
		return result;
	}

	nfa kleene(nfa to_close)
	{
		const auto old_initial_id = to_close.initial_state_id_;
		const auto new_initial_id = to_close.states_.size();
		const auto new_end_id = to_close.states_.size()+1;
		
		state new_start;
		new_start.transitions[nfa::epsilon_symbol].insert(old_initial_id);
		new_start.transitions[nfa::epsilon_symbol].insert(new_end_id);
		to_close.initial_state_id_ = new_initial_id;
		to_close.states_.push_back(std::move(new_start));

		for(auto& state: to_close.states_)
		{
			if(state.is_final)
			{
				state.is_final = false;
				state.transitions[nfa::epsilon_symbol].insert(new_end_id);
			}
		}

		state new_end;
		new_end.is_final = true;
		new_end.transitions[nfa::epsilon_symbol].insert(new_initial_id);
		to_close.states_.push_back(std::move(new_end));

		to_close.simplify();
		return to_close;
	}
	
	std::ostream& operator<<(std::ostream& out, const nfa& automaton)
	{
		out<<"digraph automaton\n";
		out<<"{\n\tranksep=2\n\trankdir=LR;\n";

		out<<"\tinit [shape = point ];\n";
		out<<"\tinit -> node"<<automaton.initial_state_id_<<";\n\n";

		for(std::size_t id = 0; id<automaton.states_.size(); ++id)
		{
			out<<"\tnode"<<id<<"[label=\"node"<<id<<"\"] [ shape = ";
			if(automaton.states_[id].is_final) out<<"double";
			out<<"circle, fillcolor=grey, stale=\"filled\"];\n";

			for(const auto& [symbol, targets]: automaton.states_[id].transitions)
			{
				const auto print_symbol = symbol==nfa::epsilon_symbol?
					"epsilon":
					symbol==nfa::wildcard_symbol?"wildcard":std::string(1,symbol);

				for(auto target_id: targets)
					out<<"\tnode"<<id<<"->node"<<target_id<<"[label=\""<<print_symbol<<"\"];\n";
			}
		}

		out<<"}\n";
		return out;
	}
}
