#ifndef SUSE_RING_BUFFER_HPP
#define SUSE_RING_BUFFER_HPP

#include <vector>

#include <cstddef>

namespace suse
{
	template <typename T>
	class ring_buffer
	{
		public:
		explicit ring_buffer(std::size_t capacity, const T& initial_value = {});

		T& operator[](std::size_t idx);
		const T& operator[](std::size_t idx) const;

		void push_back(T value);
		void pop_front();
		void clear();

		bool empty() const;
		std::size_t size() const;
		std::size_t capacity() const;
		
		private:
		std::vector<T> buffer_;
		std::size_t start_ = 0, size_ = 0;

		std::size_t to_real_index(std::size_t idx) const;
	};

	template <typename T>
	bool operator==(const ring_buffer<T>& lhs, const ring_buffer<T>& rhs);
}

#include "ring_buffer_impl.hpp"

#endif
