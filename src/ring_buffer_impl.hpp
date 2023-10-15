/*
	Never include directly!
	This is included by ring_buffer.hpp and only exists to split
	interface and implementation despite the template.
*/

namespace suse
{

template <typename T>
ring_buffer<T>::ring_buffer(std::size_t capacity, const T& initial_value):
	buffer_(capacity, initial_value)
{}

template <typename T>
T& ring_buffer<T>::operator[](std::size_t idx)
{
	return buffer_[to_real_index(idx)];
}

template <typename T>
const T& ring_buffer<T>::operator[](std::size_t idx) const
{
	return buffer_[to_real_index(idx)];
}

template <typename T>
void ring_buffer<T>::push_back(T value)
{
	buffer_[to_real_index(size_++)] = std::move(value);
}

template <typename T>
void ring_buffer<T>::pop_front()
{
	start_ = (start_+1)%buffer_.size();
	--size_;
}

template <typename T>
void ring_buffer<T>::clear()
{
	start_ = size_ = 0;
}

template <typename T>
bool ring_buffer<T>::empty() const
{
	return size_==0;
}

template <typename T>
std::size_t ring_buffer<T>::size() const
{
	return size_;
}

template <typename T>
std::size_t ring_buffer<T>::capacity() const
{
	return buffer_.size();
}

template <typename T>
std::size_t ring_buffer<T>::to_real_index(std::size_t idx) const
{
	return (start_+idx)%buffer_.size();
}

template <typename T>
bool operator==(const ring_buffer<T>& lhs, const ring_buffer<T>& rhs)
{
	if(lhs.capacity()!=rhs.capacity() || lhs.size()!=rhs.size()) return false;
	for(std::size_t i=0;i<lhs.size();++i)
	{
		if(lhs[i]!=rhs[i])
			return false;
	}

	return true;
}

}
