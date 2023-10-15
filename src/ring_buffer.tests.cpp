#include "ring_buffer.hpp"

#include <doctest/doctest.h>

#include <queue>

TEST_SUITE("suse::ring_buffer")
{
	TEST_CASE("simple")
	{
		std::deque<char> queue;
		suse::ring_buffer<char> buffer(10);

		for(std::size_t loop_idx=0;auto c: "ajsdfowjoasdfasdfjojwrhgolj0töjeht4jjo490jaoöj04jrjg04jt0q4jpjgoj43höqojgperj0jgöjerjh5nslkmfaodof")
		{
			CAPTURE(loop_idx++);

			if(queue.size()>=buffer.capacity())
				queue.pop_front();

			if(buffer.size()>=buffer.capacity())
				buffer.pop_front();
			
			queue.push_back(c);
			buffer.push_back(c);

			REQUIRE(queue.size()==buffer.size());
			
			for(std::size_t idx=0;idx<queue.size();++idx)
				REQUIRE(queue[idx]==buffer[idx]);
				
		}
	}
}
