#include "regex.hpp"

#include <fmt/core.h>
#include <fmt/format.h>

#include <algorithm>
#include <initializer_list>
#include <optional>

namespace
{
	enum class token_type
	{
		wildcard,
		optional_repetition,
		required_repetition,
		option,
		alternative,
		open_parenthesis,
		close_parenthesis,
		character,
		end_of_input
	};

	std::string_view to_string(token_type type)
	{
		using enum token_type;
		switch(type)
		{
			case wildcard: return "wildcard('.')";
			case optional_repetition: return "optional repetition('*')";
			case required_repetition: return "required repetition('+')";
			case option: return "option('?')";
			case alternative: return "alternative('|')";
			case open_parenthesis: return "open parenthesis('(')";
			case close_parenthesis: return "close parenthesis(')')";
			case character: return "character";
			case end_of_input: return "end of input";
		}
		
		return "invalid token type";
	}

	struct token
	{
		token_type type;
		char symbol;
		std::size_t position;
	};
}

template <>
struct fmt::formatter<token_type>: fmt::formatter<std::string_view>
{
	auto format(token_type type, format_context& ctx) const
	{
		return formatter<std::string_view>::format(to_string(type),ctx);
	}
};

template <>
struct fmt::formatter<token>
{
	auto parse(format_parse_context& ctx)
	{
		return ctx.begin();
	}
	
	auto format(const token& t, format_context& ctx) const
	{
		if(t.type==token_type::character)
			return fmt::format_to(ctx.out(),"'{}'",t.symbol);
		
		return fmt::format_to(ctx.out(),"{}",t.type);
	}
};

namespace
{
	class lexer
	{
		public:
		explicit lexer(std::string_view input):
			input_{input},
			next_token_{tokenize_next()}
		{}

		token consume();
		std::optional<token> consume_if(std::initializer_list<token_type> expected);
		token consume_and_check(std::initializer_list<token_type> expected);
		token consume_and_check(std::initializer_list<token_type> expected, std::size_t reported_position);

		private:
		std::string_view input_;
		std::size_t input_position_{};

		token next_token_;

		token tokenize_next();
	};

	token lexer::consume()
	{
		auto current = next_token_;
		next_token_ = tokenize_next();
		return current;
	}
	
	std::optional<token> lexer::consume_if(std::initializer_list<token_type> expected)
	{
		if(std::find(expected.begin(),expected.end(),next_token_.type)!=expected.end())
			return consume();
		
		return std::nullopt;
	}
	
	token lexer::consume_and_check(std::initializer_list<token_type> expected)
	{
		return consume_and_check(expected,next_token_.position);
	}

	token lexer::consume_and_check(std::initializer_list<token_type> expected, std::size_t reported_position)
	{
		auto current = consume();
		if(std::find(expected.begin(),expected.end(),current.type)==expected.end())
		{
			if(expected.size()==1)
				throw suse::regex_parse_error(fmt::format("Expected {}, but got {}",fmt::join(expected,", "),current),reported_position);

			throw suse::regex_parse_error(fmt::format("Expected one of {{{}}}, but got {}",fmt::join(expected,", "),current),reported_position);
		}

		return current;
	}

	token lexer::tokenize_next()
	{
		if(input_position_>=input_.size())
			return {token_type::end_of_input,'\0',input_position_};

		switch(char symbol=input_[input_position_++];symbol)
		{
			case '(': return token{token_type::open_parenthesis,symbol,input_position_-1};
			case ')': return token{token_type::close_parenthesis,symbol,input_position_-1};
			case '.': return token{token_type::wildcard,symbol,input_position_-1};
			case '|': return token{token_type::alternative,symbol,input_position_-1};
			case '*': return token{token_type::optional_repetition,symbol,input_position_-1};
			case '+': return token{token_type::required_repetition,symbol,input_position_-1};
			case '?': return token{token_type::option,symbol,input_position_-1};
			case '\\':
			{
				if(input_position_>=input_.size())
					throw suse::regex_parse_error("Unescaped '\\' at end of input. To include a single backslash, double it up like this: '\\\\'",input_position_);
				return token{token_type::character,input_[input_position_++],input_position_-1};
			}
			default: return token{token_type::character,symbol,input_position_-1};
		}
	}
	
	suse::nfa parse_repetition(lexer& lex, suse::nfa to_repeat)
	{
		using enum token_type;
		
		while(auto rep=lex.consume_if({optional_repetition,required_repetition,option}))
		{
			switch(rep->type)
			{
				case optional_repetition:
				{
					to_repeat = kleene(std::move(to_repeat));
					break;
				}
				case required_repetition:
				{
					to_repeat = concatenate(to_repeat,kleene(to_repeat));
					break;
				}
				case option:
				{
					to_repeat = union_automaton(std::move(to_repeat),suse::nfa::singleton(suse::nfa::epsilon_symbol));
					break;
				}
				
				default: break;
			}
		}
		return to_repeat;
	};

	
	suse::nfa parse_union(lexer& lex);
	
	suse::nfa parse_concatenation(lexer& lex)
	{
		using enum token_type;
		
		auto result = suse::nfa::singleton(suse::nfa::epsilon_symbol);	
		while(auto token = lex.consume_if({open_parenthesis,wildcard,character}))
		{
			if(token->type==open_parenthesis)
			{
				auto inner = parse_union(lex);
				lex.consume_and_check({token_type::close_parenthesis},token->position);
				result = concatenate(result,parse_repetition(lex,std::move(inner)));
			}
			else
			{
				const auto symbol = token->type==wildcard?suse::nfa::wildcard_symbol:token->symbol;
				auto inner = suse::nfa::singleton(symbol); 
				result = concatenate(result,parse_repetition(lex,std::move(inner)));
			}
		}

		return result;
	};
	
	suse::nfa parse_union(lexer& lex)
	{
		auto lhs = parse_concatenation(lex);
		while(lex.consume_if({token_type::alternative}))
		{
			auto rhs = parse_concatenation(lex);
			lhs = union_automaton(std::move(lhs),std::move(rhs));
		}

		return lhs;
	};
}

using namespace suse;

nfa suse::parse_regex(std::string_view input)
{
	lexer lex{input};

	auto result = parse_union(lex);
	lex.consume_and_check({token_type::end_of_input});

	return result;
}
