#include <span>


std::span<int> from_ptr(int* ptr, size_t size) {
    std::span<int> ret(ptr, size);
    ret.data();
    return ret;
}