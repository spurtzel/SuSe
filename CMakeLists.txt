cmake_minimum_required(VERSION 3.12.0)
project(summary_selector VERSION 0.0.1)

if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

set(LIBRARY_OUTPUT_PATH "${CMAKE_BINARY_DIR}")
set(EXECUTABLE_OUTPUT_PATH "${CMAKE_BINARY_DIR}")

include(FetchContent)
set(FETCHCONTENT_QUIET FALSE)

FetchContent_Declare(
	doctest
	GIT_REPOSITORY https://github.com/doctest/doctest.git
	GIT_TAG v2.4.11
	GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(doctest)

FetchContent_Declare(
	nanobench
	GIT_REPOSITORY https://github.com/martinus/nanobench.git
	GIT_TAG v4.3.11
	GIT_SHALLOW TRUE
)

FetchContent_MakeAvailable(nanobench)

set(BOOST_INCLUDE_LIBRARIES multiprecision)
set(BOOST_ENABLE_CMAKE ON)

FetchContent_Declare(
	Boost
	URL https://github.com/boostorg/boost/releases/download/boost-1.82.0/boost-1.82.0.7z
	USES_TERMINAL_DOWNLOAD TRUE 
	GIT_PROGRESS TRUE   
	DOWNLOAD_NO_EXTRACT FALSE
	SYSTEM
)
FetchContent_MakeAvailable(Boost)

FetchContent_Declare(
	fmt
	GIT_REPOSITORY https://github.com/fmtlib/fmt.git
	GIT_TAG 10.0.0
	GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(fmt)

set(CXXOPTS_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(CXXOPTS_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(CXXOPTS_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
set(CXXOPTS_ENABLE_WARNINGS OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
	cxxopts
	GIT_REPOSITORY https://github.com/jarro2783/cxxopts.git
	GIT_TAG v3.1.1
	GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(cxxopts)

set(suse_sources

	src/edgelist.hpp
	src/edgelist.cpp

	src/event.hpp

	src/eviction_strategies.hpp
	src/eviction_strategies_impl.hpp

	src/execution_state_counter_impl.hpp
	src/execution_state_counter.hpp

	src/nfa.cpp
	src/nfa.hpp

	src/regex.cpp
	src/regex.hpp

	src/ring_buffer.hpp
	src/ring_buffer_impl.hpp

	src/summary_selector.hpp
	src/summary_selector_impl.hpp
)

add_executable(regex_compiler

	${suse_sources}
	src/regex_compiler.cpp
)

if(MSVC)
	target_compile_options(regex_compiler PRIVATE /W4)
else()
	target_compile_options(regex_compiler PRIVATE -Wall -pedantic -Werror)
endif()

target_compile_definitions(regex_compiler PRIVATE DOCTEST_CONFIG_DISABLE)

target_link_libraries(regex_compiler PRIVATE fmt::fmt doctest cxxopts)
set_property(TARGET regex_compiler PROPERTY CXX_STANDARD 20)

add_executable(summary_selector

	${suse_sources}

	src/summary_selector.cpp
)

if(MSVC)
	target_compile_options(summary_selector PRIVATE /W4)
else()
	target_compile_options(summary_selector PRIVATE -Wall -pedantic -Werror)
endif()

target_compile_definitions(summary_selector PRIVATE DOCTEST_CONFIG_DISABLE)

target_link_libraries(summary_selector PRIVATE fmt::fmt Boost::multiprecision doctest cxxopts)
set_property(TARGET summary_selector PROPERTY CXX_STANDARD 20)

file(GLOB test_sources CONFIGURE_DEPENDS src/*.tests.cpp)
add_executable(tests

	${suse_sources}
	${test_sources}

	src/test_main.cpp
)
target_link_libraries(tests PRIVATE fmt::fmt Boost::multiprecision doctest)
set_property(TARGET tests PROPERTY CXX_STANDARD 20)

file(GLOB benchmark_sources CONFIGURE_DEPENDS src/*.bench.cpp)
add_executable(benchmarks

	${suse_sources}
	${benchmark_sources}

	src/benchmark_main.cpp
)
target_link_libraries(benchmarks PRIVATE fmt::fmt Boost::multiprecision doctest nanobench)
set_property(TARGET benchmarks PROPERTY CXX_STANDARD 20)


add_executable(match_enumerator

	${suse_sources}
	src/match_enumerator.cpp
)

if(MSVC)
	target_compile_options(match_enumerator PRIVATE /W4)
else()
	target_compile_options(match_enumerator PRIVATE -Wall -pedantic -Werror)
endif()

target_compile_definitions(match_enumerator PRIVATE DOCTEST_CONFIG_DISABLE)

target_link_libraries(match_enumerator PRIVATE fmt::fmt Boost::multiprecision cxxopts)
set_property(TARGET match_enumerator PROPERTY CXX_STANDARD 20)


file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/append_to_report.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/evaluation_timestamp_generator.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/event_stream_generator.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/evaluation_script.sh DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/run_test.sh DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

