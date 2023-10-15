#include "nfa.hpp"
#include "regex.hpp"

#include <cxxopts.hpp>

#include <fmt/color.h>
#include <fmt/format.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

namespace
{
	std::optional<suse::nfa> try_compile(std::string_view line)
	{
		try
		{
			return suse::parse_regex(line);
		}
		catch(const suse::regex_parse_error& error)
		{
			const auto prefix = line.substr(0,error.location);
			const auto error_char = error.location<line.size()?line.substr(error.location,1):std::string_view{};
			const auto suffix = error.location+1<line.size()?line.substr(error.location+1):std::string_view{};
			fmt::print(fmt::fg(fmt::color::red),"\nAt position {}:\n\n",error.location);
			fmt::print("{}{}{}\n{: >{}}\n",prefix,fmt::styled(error_char,fmt::fg(fmt::color::red)),suffix,"^",error.location+1);
			fmt::print(fmt::fg(fmt::color::red),"Parse error: ");
			fmt::print("{}\n",error.what());

			return std::nullopt;
		}
	}

	void filter(const suse::nfa& nfa)
	{	
		for(std::string line; std::getline(std::cin,line);)
		{
			if(nfa.check(line))
				fmt::print("{}\n",line);
		}
	}
}

int main(int argc, char* argv[]) try
{
	cxxopts::Options options("regex_compiler", "Transforms a regex into a corresponding NFA to draw and use.");
	options.add_options()
		("regex,r","Regex to convert/evaluate",cxxopts::value<std::string>())
		("output,o","File to write the graphviz-dot representation of the compiled NFA to",cxxopts::value<std::string>())
		("evaluate,e","Pretend to be a cheap imitation of grep: read lines from stdin and print those matching the given regex")
		("interactive,i","Repeatedly wait for lines from stdin, parse them and output the compiled automaton to a file")
		("help,h","Display this help meassage");

	options.parse_positional("regex");
	options.positional_help("regex");

	const auto parsed_args = options.parse(argc,argv);

	if(parsed_args.count("help")>0 || argc<2)
	{
		fmt::print("{}",options.help());
		return 0;
	}

	if(parsed_args.count("regex")==0 && parsed_args.count("interactive")==0)
	{
		fmt::print(stderr,"You need to provide a regex for non-interactive mode\n");
		return 1;
	}

	if(parsed_args.count("evaluate")>0 && parsed_args.count("interactive")>0)
	{
		fmt::print(stderr,"Interactive mode and evaluation mode mode are mutually exclusive\n");
		return 1;
	}

	std::optional<suse::nfa> current_nfa = std::nullopt;
	
	const std::optional<std::filesystem::path> target_filename = parsed_args.count("output")?
		parsed_args["output"].as<std::string>():
		std::optional<std::filesystem::path>{};
	
	const auto try_save = [&]()
	{
		if(target_filename && current_nfa)
		{
			std::ofstream out{*target_filename};
			out<<*current_nfa;
		}
	};

	if(parsed_args.count("regex")>0)
		current_nfa = try_compile(parsed_args["regex"].template as<std::string>());
	try_save();

	if(parsed_args.count("evaluate")>0 && current_nfa)
		filter(*current_nfa);

	if(parsed_args.count("interactive")>0)
	{
		for(std::string line; std::getline(std::cin,line);)
		{
			if((current_nfa = try_compile(line)))
				try_save();
		}
	}
	
	return 0;
}
catch(const cxxopts::exceptions::exception& e)
{
	fmt::print(stderr,"Error parsing arguments: {}\n", e.what());
	return 1;
}
