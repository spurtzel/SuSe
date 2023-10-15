#include "edgelist.hpp"

namespace suse
{
	std::span<const edge> edgelist::edges_for(char symbol) const
	{
		const auto range = character_to_range_[symbol];
		return {edges_.begin()+range.start,range.size};
	}
	
	edgelist compute_edges_per_character(const nfa& automaton)
	{
		std::unordered_map<char,std::vector<edge>> collected_edges;
		for(std::size_t source_id=0;source_id<automaton.number_of_states();++source_id)
		{
			const auto& state = automaton.states()[source_id];
			for(const auto& [symbol,targets]: state.transitions)
			{
				for(auto target: targets)
					collected_edges[symbol].push_back({source_id,target});
			}
		}

		edgelist result;

		for(const auto& [symbol,edges]: collected_edges)
		{
			result.character_to_range_[symbol] = {result.edges_.size(),edges.size()};
			result.edges_.insert(result.edges_.end(),edges.begin(),edges.end());
		}
		
		return result;
	}
}
